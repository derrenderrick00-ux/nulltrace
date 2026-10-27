"""Pygame-CE desktop UI for NULLTRACE v1.5.0-rc1 (education + cinematic investigations).

No game action launches an unrestricted shell command. Real labs are explicit,
loopback-only or offline, and isolated from simulated terminal input.
"""
from __future__ import annotations
from pathlib import Path
import os

from nulltrace.core.content import Curriculum
from nulltrace.education.lessons import LessonLibrary, STAGE_KEYS
from nulltrace.core.session import Session
from nulltrace.persistence.store import Store
from nulltrace.story.scenes import CHAPTERS, INTRO
from nulltrace.labs.terminal import VirtualTerminal
from nulltrace.labs.practical import LAB_MISSIONS,run_lab
from nulltrace.network.simulator import HOSTS,route
from nulltrace.ui.operator_animation import draw_operator, advance_position
from nulltrace.story.endings import resolve_ending
from nulltrace.cinematics.timeline import CinematicLibrary, Timeline
from nulltrace.cinematics.sets import draw_set
from nulltrace.investigations.casebook import Casebook, CaseSession
from nulltrace.network.journey import PacketJourney

WIDTH,HEIGHT=1180,720
BG=(7,14,26);PANEL=(14,26,42);CARD=(22,39,57);BORDER=(42,71,88)
TEXT=(233,243,246);MUTED=(154,174,185);ACCENT=(64,214,209);GOLD=(240,194,98);GOOD=(120,218,160);BAD=(240,110,116)

class Game:
    def __init__(self, pygame, qa=False, store=None, curriculum=None):
        self.pg=pygame
        pygame.init()
        self.screen=pygame.display.set_mode((WIDTH,HEIGHT),pygame.RESIZABLE)
        pygame.display.set_caption('NULLTRACE | Cinematic Investigations — v1.5 RC1')
        self.canvas=pygame.Surface((WIDTH,HEIGHT))
        self.f={
            'small':pygame.font.SysFont('DejaVu Sans',15),
            'normal':pygame.font.SysFont('DejaVu Sans',18),
            'medium':pygame.font.SysFont('DejaVu Sans',22,bold=True),
            'large':pygame.font.SysFont('DejaVu Sans',37,bold=True),
        }
        self.store=store or Store()
        self.curriculum=curriculum or Curriculum()
        self.lessons=LessonLibrary(self.curriculum.root,self.curriculum)
        self.cinematics=CinematicLibrary(self.curriculum.root)
        self.casebook=Casebook(self.curriculum.root)
        self.cutscene=Timeline(self.cinematics.get(1))
        self.case_session=CaseSession(self.casebook.get(1))
        self.case_feedback=''
        self.journey=PacketJourney(1)
        self.stage=0;self.lesson_scroll=0;self.diagram_hop=0
        self.practice_feedback='';self.practice_ok=False
        self.field_note='';self.qa_stages={}
        self.qa=qa
        self.page='home'
        self.chapter=1;self.mid='CH01-M01'
        self.buttons=[]
        self.profile_id=None
        self.session=None
        self.name='Alex';self.codename='Ghost';self.appearance='hoodie'
        self.focus='name';self.error='';self.notice=''
        self.qa_story_choices={}
        self.selected_answer=None;self.correct=False;self.feedback=''
        self.terminal=VirtualTerminal();self.command='';self.term_lines=['NULLTRACE SAFE TERMINAL — typed commands are SIMULATED. Try help.']
        self.node='workstation-07'
        self.gateway_online=True
        self.case_note=''
        self.running=True
        self.room_x=695.0;self.room_y=496.0;self.room_moving=False
        self.room_facing=1;self.reduced_motion=False
        if self.store.players():self.select_player(self.store.players()[0]['id'])

    def close(self):
        self.store.close()
        self.pg.quit()

    def select_player(self,pid):
        self.profile_id=pid
        self.session=Session(self.curriculum,self.store,pid,self.qa)
        profile=self.store.player(pid)
        self.name=profile['name'];self.codename=profile['codename']
        self.appearance=profile['appearance']
        self.error=''

    def new_profile(self):
        try:
            pid=self.store.create_player(self.name,self.codename,self.appearance)
            self.select_player(pid)
            self.page='story';self.chapter=1
        except ValueError as exc:self.error=str(exc)

    def _write(self,msg,x,y,font='normal',color=TEXT,max_width=None,max_lines=99,line_height=None):
        face=self.f[font];limit=max_width or 3000
        line_height=line_height or face.get_linesize()+5
        words=str(msg).split()
        lines=[];line=''
        for word in words:
            trial=f'{line} {word}'.strip()
            if face.size(trial)[0]<=limit:
                line=trial
            else:
                if line:lines.append(line)
                line=word
                # very long tokens are truncated rather than overflowing cards
                while face.size(line)[0]>limit and len(line)>1:line=line[:-1]
        if line:lines.append(line)
        for i,t in enumerate(lines[:max_lines]):
            self.canvas.blit(face.render(t,True,color),(x,y+i*line_height))
        return y+min(len(lines),max_lines)*line_height

    def _rect(self,x,y,w,h,fill=CARD,radius=12,border=BORDER):
        r=self.pg.Rect(x,y,w,h)
        self.pg.draw.rect(self.canvas,fill,r,border_radius=radius)
        if border:self.pg.draw.rect(self.canvas,border,r,1,border_radius=radius)
        return r

    def _button(self,label,x,y,w,h,action,enabled=True,highlight=False):
        r=self._rect(x,y,w,h,ACCENT if highlight else CARD,9,ACCENT if enabled and highlight else BORDER)
        text_color=BG if highlight else TEXT if enabled else MUTED
        face=self.f['normal'];short=label
        while face.size(short)[0]>w-16 and len(short)>2:short=short[:-2]+'…'
        surf=face.render(short,True,text_color)
        self.canvas.blit(surf,(x+(w-surf.get_width())//2,y+(h-surf.get_height())//2))
        if enabled:self.buttons.append((r,action))

    def _header(self):
        self.canvas.fill(BG)
        self._write('N U L L T R A C E',28,22,'large',ACCENT)
        self._write('THE CYBERSECURITY CHRONICLES',31,65,'small',MUTED)
        self._write('CINEMATIC v1.5 RC1  •  100 LESSONS',817,20,'small',GOLD)
        self.pg.draw.line(self.canvas,BORDER,(24,96),(1156,96),1)
        if self.session:
            profile=self.store.player(self.profile_id)
            self._write(f'OPERATOR  {profile["name"]}  /  {profile["codename"]}',820,56,'small',MUTED)
        if self.qa:self._write('QA MODE — ALL MISSIONS OPEN / NO PROGRESS SAVED',460,65,'small',GOLD)

    def _sidebar(self):
        self._rect(23,112,218,531,PANEL,14)
        links=[('COMMAND CENTER','home'),('STORY ARCHIVE','story'),('CHAPTERS','chapters'),('ACADEMY','academy'),('SAFE TERMINAL','terminal'),('NETWORK MAP','network'),('EVIDENCE BOARD','evidence'),('TOOL LABS','tools'),('OPERATOR','profile')]
        for i,(name,page) in enumerate(links):
            self._button(name,35,128+i*52,194,44,lambda p=page:self.navigate(p),True,self.page==page)
        self._write('OFFLINE-FIRST / LOCAL SAVES',35,616,'small',MUTED,max_width=190)

    def _panel(self,title,kicker=''):
        self._rect(255,112,901,531,PANEL,14)
        self._write(title,282,131,'medium',ACCENT,max_width=850)
        if kicker:self._write(kicker,284,167,'small',MUTED,max_width=840)

    def _footer(self):
        self.pg.draw.line(self.canvas,BORDER,(24,661),(1156,661),1)
        self._write('ESC: chapters / back    •    Click buttons to navigate    •    All terminal commands are simulated',30,677,'small',MUTED,max_width=1050)

    def navigate(self,page):
        if page!='profile' and self.session is None:self.page='profile';return
        self.page=page
        self.notice='';self.error=''

    def render(self):
        self.buttons=[]
        self._header();self._sidebar()
        getattr(self,'draw_'+self.page)()
        if self.error and self.page!='lesson':self._write(self.error,270,614,'small',BAD,max_width=850)
        if self.notice:self._write(self.notice,270,614,'small',GOOD,max_width=850)
        self._footer()
        newsize=self.screen.get_size()
        if newsize==(WIDTH,HEIGHT):self.screen.blit(self.canvas,(0,0))
        else:self.pg.transform.smoothscale(self.canvas,newsize,self.screen)
        self.pg.display.flip()

    def draw_home(self):
        self._panel('MERIDIAN OPERATIONS // SECURE BRIEFING','Year 2038 · The NEXUS system is watching the network.')
        if self.session is None:
            self._write('Create your operator identity to begin the investigation.',290,220,'medium',TEXT,max_width=800)
            self._button('CREATE OPERATOR',290,292,310,52,lambda:self.navigate('profile'),highlight=True)
            return
        c=self.session.completed
        self._write(f'{len(c)} / 100 TRAINING MISSIONS COMPLETED',290,215,'medium',GOOD,max_width=700)
        self._write('MIRROR-07 appeared in an unexplained event record. Evidence is not the same as proof.',290,267,'normal',MUTED,max_width=660,max_lines=3)
        profile=self.store.player(self.profile_id)
        draw_operator(self.pg,self.canvas,1040,329,profile['appearance'],self.pg.time.get_ticks(),scale=0.67,reduced_motion=self.reduced_motion)
        all_done=len(c)==100
        upcoming=next((m for m in self.curriculum.active if m.id not in c),self.curriculum.active[-1])
        self._rect(287,343,819,109,CARD)
        self._write('NEXT INVESTIGATION',304,356,'small',GOLD)
        self._write(f'{upcoming.id}  {upcoming.title}',304,383,'medium',TEXT,max_width=710)
        self._button('VIEW YOUR ENDING' if all_done else 'CONTINUE MISSION',290,477,270,48,lambda m=upcoming.id:self.navigate('ending') if all_done else self.open_mission(m),highlight=True)
        self._button('BROWSE CHAPTERS',578,477,270,48,lambda:self.navigate('chapters'))
        self._button('OPERATIONS FLOOR',864,477,242,48,lambda:self.navigate('operator_room'))
        self._write('100 Academy lessons, 10 replayable chapter cinematics, 10 synthetic evidence investigations.',289,566,'small',MUTED,max_width=805,max_lines=2)

    def draw_profile(self):
        self._panel('CREATE / SELECT OPERATOR','Alex / Ghost / hoodie are editable examples, never mandatory identities.')
        if self.store.players():
            self._write('EXISTING OPERATORS',283,200,'small',GOLD)
            for i,row in enumerate(self.store.players()[:3]):
                label=f'{row["name"]}  /  {row["codename"]}  •  {row["appearance"]}'
                self._button(label,283,224+i*49,790,42,lambda pid=row['id']:self._choose_profile(pid))
        else:self._write('No saved operator yet.',283,202,'small',MUTED)
        y=390 if self.store.players() else 258
        self._write('NEW OPERATOR',283,y,'small',GOLD)
        self._input_box('NAME',self.name,'name',285,y+35,344)
        self._input_box('CODENAME',self.codename,'codename',648,y+35,344)
        self._write('APPEARANCE',285,y+102,'small',MUTED)
        for i,a in enumerate(('hoodie','analyst','technician')):
            self._button(a.upper(),285+i*191,y+126,178,39,lambda a=a:self._set_appearance(a),highlight=self.appearance==a)
        self._button('CREATE & ENTER STORY',864,y+125,230,40,self.new_profile,highlight=True)
        # Small, animated preview of the appearance selection, no extra art assets.
        draw_operator(self.pg,self.canvas,1051,y+118,self.appearance,self.pg.time.get_ticks(),
                      scale=0.39,reduced_motion=self.reduced_motion)

    def _choose_profile(self,pid):
        self.select_player(pid);self.page='home'
    def _set_appearance(self,a):self.appearance=a
    def _input_box(self,label,value,field,x,y,w):
        self._write(label,x,y-22,'small',MUTED)
        self._rect(x,y,w,42,CARD,7,ACCENT if self.focus==field else BORDER)
        self._write(value or '(type here)',x+11,y+10,'normal',TEXT,max_width=w-20,max_lines=1)
        self.buttons.append((self.pg.Rect(x,y,w,42),lambda f=field:self._set_focus(f)))
    def _set_focus(self,field):self.focus=field

    def draw_story(self):
        name,title,location,first,last=(self.chapter,)+CHAPTERS.get(self.chapter,CHAPTERS[1])
        self._panel(f'ACT {1 if name<=3 else 2 if name<=7 else 3} / CHAPTER {name:02d} — {title}', f'{location} // STORY BRIEFING')
        self._button('WATCH CINEMATIC',289,186,206,29,self._start_cinematic)
        self._button('OPEN CHAPTER CASE',515,186,231,29,self._start_case)
        self._button('PACKET JOURNEY',768,186,231,29,self._start_journey)
        self._rect(290,221,811,262,(12,31,44),10)
        self._write(first,314,249,'medium',TEXT,max_width=560,max_lines=5,line_height=29)
        self._write(last,314,378,'normal',ACCENT,max_width=560,max_lines=4,line_height=29)
        if self.session:
            profile=self.store.player(self.profile_id)
            draw_operator(self.pg,self.canvas,979,465,profile['appearance'],self.pg.time.get_ticks(),scale=0.88,reduced_motion=self.reduced_motion)
            self._write(profile['codename'].upper(),943,480,'small',ACCENT,max_width=135,max_lines=1)
        self._button('ENTER INVESTIGATION',295,516,290,48,lambda:self._open_chapter(self.chapter),highlight=True)
        self._button('CHOOSE ANOTHER CHAPTER',608,516,315,48,lambda:self.navigate('chapters'))
        if self.chapter==10 and self.session:
            self._button('CHOOSE DISCLOSURE ROUTE',294,567,371,43,lambda:self.navigate('disclosure'),highlight=True)
            route=(self.qa_story_choices if self.qa else self.store.choices(self.profile_id)).get('disclosure_route','not selected')
            self._write(f'Current route: {route}',687,582,'small',MUTED,max_width=384)
        if self.chapter in (1,5,9) and self.session:
            label = 'FIRST REPORT' if self.chapter==1 else 'EVIDENCE REVIEW' if self.chapter==5 else 'EVIDENCE PRESERVATION'
            self._write(label,299,576,'small',GOLD)
            self._button('REPORT THROUGH CHANNELS',465,569,290,37,lambda:self._story_decision('report'))
            self._button('VERIFY EVIDENCE FIRST',774,569,316,37,lambda:self._story_decision('verify'))
            chosen=(self.qa_story_choices if self.qa else self.store.choices(self.profile_id)).get(f'chapter{self.chapter:02d}_decision','not chosen')
            self._write(f'Recorded decision: {chosen}',304,611,'small',MUTED,max_width=620)

    def _start_cinematic(self):
        self.cutscene=Timeline(self.cinematics.get(self.chapter))
        self.page='cinematic'
        self.notice='';self.error=''

    def draw_cinematic(self):
        seq=self.cutscene.sequence
        beat=self.cutscene.beat
        self._panel(f'CINEMATIC / CHAPTER {seq.chapter:02d} — {CHAPTERS[seq.chapter][0]}',
                    f'{seq.location}   •   Beat {self.cutscene.index+1}/{len(seq.beats)}   •   Manual controls always available')
        draw_set(self.pg,self.canvas,(287,204,818,237),seq.environment,beat.shot,
                 self.pg.time.get_ticks(),self.reduced_motion)
        if self.session:
            appearance=self.store.player(self.profile_id)['appearance']
            draw_operator(self.pg,self.canvas,985,418,appearance,self.pg.time.get_ticks(),
                          scale=.70,reduced_motion=self.reduced_motion)
        self._rect(287,446,817,100,(10,25,40),8)
        speaker= self.codename.upper() if beat.speaker=='OPERATOR' else beat.speaker
        text=self.cinematics.substitute(beat.text,self.name,self.codename)
        self._write(f'{speaker}  //  {beat.shot.upper()}',304,453,'small',GOLD)
        self._write(text,304,476,'normal',TEXT,max_width=773,max_lines=3,line_height=22)
        self._button('◀ PREV',286,564,134,39,self.cutscene.previous,enabled=self.cutscene.index>0)
        self._button('NEXT ▶' if not self.cutscene.done else 'AT END',427,564,138,39,self.cutscene.advance,enabled=not self.cutscene.done)
        self._button('PAUSE' if self.cutscene.playing else 'AUTO PLAY',571,564,160,39,self._toggle_cutscene)
        self._button('RESTART',742,564,150,39,self.cutscene.restart)
        self._button('BACK TO STORY',902,564,195,39,lambda:self.navigate('story'),highlight=True)
        self._write('SPACE: next beat   •   R: restart   •   M: reduced motion   •   These are story scenes, not live evidence.',292,615,'small',MUTED,max_width=790)

    def _toggle_cutscene(self):
        self.cutscene.playing=not self.cutscene.playing and not self.reduced_motion

    def _start_case(self):
        self.case_session=CaseSession(self.casebook.get(self.chapter))
        self.case_feedback=''
        self.notice='';self.error=''
        self.page='casework'

    def _select_case_evidence(self,eid):
        self.case_session.toggle(eid)
        self.case_feedback=''

    def _choose_case_conclusion(self,index):
        self.case_session.choose(index)
        self.case_feedback=''

    def _submit_case(self):
        good, feedback=self.case_session.assess()
        self.case_feedback=('PASS: ' if good else 'REVIEW: ')+feedback
        if good and self.session and not self.qa:
            self.store.record_case(self.profile_id,self.case_session.case.id,
                                   self.case_session.conclusion,self.case_session.selected)

    def draw_casework(self):
        c=self.case_session.case
        solved=False if self.qa or not self.session else c.id in self.store.solved_cases(self.profile_id)
        self._panel(f'CASE FILE  //  {c.id} — {c.title}',
                    'Select supporting records, choose a conclusion, then submit. Case reviews are separate from missions.')
        self._write(c.briefing,291,200,'normal',TEXT,max_width=797,max_lines=2)
        self._write('EVIDENCE  —  click to include / exclude',293,250,'small',GOLD)
        for i,e in enumerate(c.evidence):
            y=274+i*42
            checked=e.id in self.case_session.selected
            lab=f'{"☑" if checked else "☐"} [{e.kind}] {e.label}'
            self._button(lab,292,y,804,37,lambda key=e.id:self._select_case_evidence(key),highlight=checked)
        y=447
        self._write('HYPOTHESIS — SELECT ONE',293,y,'small',GOLD)
        for i,choice in enumerate(c.conclusions):
            self._button(f'{i+1}. {choice}',293,469+i*35,805,31,
                         lambda i=i:self._choose_case_conclusion(i),highlight=self.case_session.conclusion==i)
        self._button('VERIFY CASE',292,595,208,35,self._submit_case,highlight=True)
        self._button('STORY',1002,595,101,35,lambda:self.navigate('story'))
        if self.case_feedback:
            self._write(self.case_feedback,517,596,'small',GOOD if self.case_feedback.startswith('PASS:') else BAD,max_width=470,max_lines=2)
        if solved:self._write('VERIFIED IN THIS PROFILE',826,256,'small',GOOD,max_width=260)

    def _start_journey(self):
        self.journey=PacketJourney(self.chapter)
        self.notice='';self.error=''
        self.page='journey'

    def draw_journey(self):
        j=self.journey
        self._panel(f'PACKET JOURNEY // {j.name.upper()}',
                    f'CH{j.chapter:02d}  •  SIMULATED TRAFFIC / NOT LIVE CAPTURE  •  Gateway {"ONLINE" if j.gateway_online else "OFFLINE"}')
        hops=j.hops
        x0=340;xspan=710
        xs=[int(x0+i*xspan/max(1,len(hops)-1)) for i in range(len(hops))]
        y=380
        for i in range(len(hops)-1):
            self.pg.draw.line(self.canvas,GOOD if i<j.index else BORDER,(xs[i]+27,y),(xs[i+1]-27,y),4)
        for i,h in enumerate(hops):
            active=i<=j.index
            self.pg.draw.circle(self.canvas,ACCENT if active else CARD,(xs[i],y),29)
            self.pg.draw.circle(self.canvas,BORDER,(xs[i],y),29,2)
            self._write(str(i+1),xs[i]-5,y-8,'normal',BG if active else TEXT)
            self._write(h.label, xs[i]-78,y+44,'small',TEXT,max_width=155,max_lines=1)
            self._write(h.address,xs[i]-78,y+65,'small',MUTED,max_width=155,max_lines=1)
        h=j.current
        self._rect(294,215,798,97,CARD)
        self._write(f'CURRENT HOP {j.index+1}/{len(hops)}: {h.label.upper()}',312,231,'medium',GOLD)
        self._write(h.note,312,267,'small',TEXT,max_width=763,max_lines=2)
        self._button('STEP',294,503,148,44,j.step,enabled=not j.at_end,highlight=True)
        self._button('PAUSE' if j.playing else 'AUTO PLAY',455,503,166,44,self._toggle_journey)
        self._button('RESET',632,503,145,44,j.reset)
        self._button('GATEWAY ON/OFF',786,503,306,44,j.toggle_gateway)
        self._write('Time steps demonstrate packet routing concepts, not actual captures or host addresses.',298,569,'small',MUTED,max_width=787)
        self._button('RETURN TO NETWORK',295,593,275,42,lambda:self.navigate('network'))
        self._button('CHAPTER CASE',586,593,249,42,self._start_case)

    def _toggle_journey(self):
        self.journey.playing=not self.journey.playing

    def _story_decision(self,value):
        key=f'chapter{self.chapter:02d}_decision'
        if self.qa:self.qa_story_choices[key]=value
        else:self.store.set_choice(self.profile_id,key,value)
        self.notice=''

    def _open_chapter(self,chapter):self.chapter=chapter;self.page='missions'

    def draw_chapters(self):
        self._panel('THE NEXUS INVESTIGATION', 'Ten chapters • 100 missions • prerequisities control normal progression.')
        c=self.session.completed if self.session else set()
        for n in range(1,11):
            row=(n-1)//2;col=(n-1)%2
            x=285+col*421;y=202+row*78
            title=CHAPTERS[n][0]
            count=sum(f'CH{n:02d}-M{i:02d}' in c for i in range(1,11))
            label=f'CH {n:02d}  {title}   {count}/10'
            self._button(label,x,y,405,59,lambda n=n:self._open_chapter(n),enabled=True)

    def draw_academy(self):
        self._panel('CYBERSECURITY ACADEMY / 100 LESSONS',
                    'Each mission has 9 independent study stages. Previous mission completions are preserved.')
        if self.qa:
            counts={n:0 for n in range(1,11)}
            for (pid,mid),steps in self.qa_stages.items():
                if pid==self.profile_id:counts[int(mid[2:4])]+=len(steps)
        else:counts=self.store.lesson_summary(self.profile_id)
        total=sum(counts.values())
        self._write(f'RECORDED STAGES: {total}/900  •  Lesson review is separate from mission competence.',
                    289,198,'normal',GOOD,max_width=780)
        for n in range(1,11):
            y=230+(n-1)*36
            chapter=CHAPTERS[n][0]
            count=counts.get(n,0)
            self._write(f'CH{n:02d} {chapter}',292,y,'small',TEXT,max_width=330)
            self._rect(630,y+1,266,15,BORDER,3,border=None)
            if count:self._rect(630,y+1,int(266*count/90),15,GOOD,3,border=None)
            self._write(f'{count}/90',917,y-2,'small',GOLD)
            self._button('OPEN',1003,y-8,96,31,lambda n=n:self._open_chapter(n))

    def draw_missions(self):
        chapter=self.chapter
        title=CHAPTERS[chapter][0]
        self._panel(f'CHAPTER {chapter:02d} — {title}','Nine-stage lessons + independent assessment • old mission completions remain intact.')
        completed=self.session.completed
        for index,m in enumerate(self.curriculum.chapter(chapter)):
            y=194+index*43
            unlocked=self.session.can_start(m.id)
            suffix='✓' if m.id in completed else '◈' if unlocked else '🔒'
            text=f'{suffix}  {m.id}   {m.title}'
            self._button(text,283,y,789,37,lambda m=m:self.open_mission(m.id),enabled=unlocked)
        self._button('STORY BRIEFING',900,150,202,32,lambda:self.navigate('story'))

    def open_mission(self,mid):
        if not self.session.can_start(mid):return
        self.mid=mid;self.chapter=int(mid[2:4]);self.page='lesson'
        self.selected_answer=None;self.correct=False;self.feedback='';self.notice=''
        done=self._done_stages(mid)
        self.stage=next((i for i in range(9) if i not in done),8)
        self.lesson_scroll=0;self.diagram_hop=0
        self.practice_feedback='';self.practice_ok=6 in done
        self.field_note='' if self.qa else self.store.lesson_note(self.profile_id,mid)

    def _done_stages(self,mid):
        if not self.session:return set()
        if self.qa:return self.qa_stages.get((self.profile_id,mid),set())
        return self.store.stages_done(self.profile_id,mid)

    def _complete_stage(self,stage=None,advance=True):
        ix=self.stage if stage is None else stage
        if ix==6 and not self.practice_ok:
            self.error='Answer the practice check before marking this stage complete.'
            return
        if ix==7 and len(self.field_note.strip())<20:
            self.error='Write a short evidence note (20+ characters) before continuing.'
            return
        if self.qa:
            self.qa_stages.setdefault((self.profile_id,self.mid),set()).add(ix)
        else:
            if ix==7:self.store.save_lesson_note(self.profile_id,self.mid,self.field_note)
            self.store.mark_stage(self.profile_id,self.mid,ix)
        self.error='';self.notice=''
        if ix<8 and advance:self._go_stage(ix+1)

    def _go_stage(self,index):
        if not 0<=index<9:return
        self.stage=index;self.lesson_scroll=0;self.diagram_hop=0
        self.practice_feedback='';self.practice_ok=6 in self._done_stages(self.mid)
        self.notice='';self.error=''

    def _practice_answer(self,index):
        m=self.curriculum.get(self.mid)
        correct,explanation=self.curriculum.checked_response(m,index)
        self.practice_feedback=('Correct! Stage recorded. ' if correct else 'Try again after reviewing stage 3. ')+explanation
        self.practice_ok=correct
        if correct:self._complete_stage(6,advance=False)

    def _wrap_lines(self,message,font,max_width):
        face=self.f[font]
        result=[]
        for paragraph in str(message).split('\n'):
            if not paragraph.strip():
                result.append('');continue
            line=''
            for word in paragraph.split():
                # Break overly long non-space tokens, don't lose evidence values.
                segments=[]
                remaining=word
                while remaining and face.size(remaining)[0]>max_width:
                    hi=len(remaining)
                    lo=1
                    while lo<hi:
                        mid=(lo+hi+1)//2
                        if face.size(remaining[:mid])[0]<=max_width:lo=mid
                        else:hi=mid-1
                    segments.append(remaining[:max(1,lo)])
                    remaining=remaining[max(1,lo):]
                if remaining:segments.append(remaining)
                for part in segments:
                    trial=f'{line} {part}'.strip()
                    if face.size(trial)[0]<=max_width:line=trial
                    else:
                        if line:result.append(line)
                        line=part
            if line:result.append(line)
        return result

    def _lesson_textbox(self,message,x,y,width,height,font='normal'):
        self._rect(x-11,y-10,width+22,height+20,(12,31,44),8)
        clip=self.canvas.get_clip()
        self.canvas.set_clip(self.pg.Rect(x,y,width,height))
        line_height=self.f[font].get_linesize()+6
        lines=self._wrap_lines(message,font,width-15)
        maxscroll=max(0,len(lines)*line_height-height+8)
        self.lesson_scroll=max(0,min(self.lesson_scroll,maxscroll))
        for i,line in enumerate(lines):
            yy=y+i*line_height-self.lesson_scroll
            if y-line_height<yy<y+height:self._write(line,x,yy,font,TEXT,max_width=width-15,max_lines=1)
        self.canvas.set_clip(clip)
        if maxscroll:
            self._write(f'SCROLL: {self.lesson_scroll//line_height+1} / {max(1,len(lines))} lines',x+width-233,y+height-18,'small',GOLD)

    def _lesson_diagram(self,lesson):
        nodes=lesson.diagram
        left,right=310,1073
        cy=465
        count=len(nodes)
        xs=[int(left+i*(right-left)/max(1,count-1)) for i in range(count)]
        for j in range(count-1):
            self.pg.draw.line(self.canvas,GOOD if j<self.diagram_hop else BORDER,(xs[j]+20,cy),(xs[j+1]-20,cy),4)
        for i,label in enumerate(nodes):
            active=i<=self.diagram_hop
            self.pg.draw.circle(self.canvas,ACCENT if active else CARD,(xs[i],cy),23)
            self.pg.draw.circle(self.canvas,BORDER,(xs[i],cy),23,2)
            self._write(str(i+1),xs[i]-5,cy-9,'normal',BG if active else TEXT)
            # Short labels never overlap neighboring diagram marks.
            words=self._wrap_lines(label,'small',min(160,int((right-left)/count)+14))
            for ln,text in enumerate(words[:2]):self._write(text,xs[i]-min(65,len(text)*4),cy+29+ln*18,'small',TEXT,max_width=144,max_lines=1)

    def draw_lesson(self):
        m=self.curriculum.get(self.mid)
        lesson=self.lessons.get(m.id)
        stage=lesson.stages[self.stage]
        done=self._done_stages(m.id)
        self._panel(f'{m.id} — {m.title}',
                    f'ACADEMY  •  {len(done)}/9 STAGES RECORDED  •  {lesson.focus}  •  Scroll mouse wheel for longer explanations')
        for i in range(9):
            label=('✓' if i in done else str(i+1))
            self._button(label,286+i*90,203,80,43,lambda i=i:self._go_stage(i),highlight=self.stage==i)
        self._write(stage['title'],292,264,'medium',GOLD,max_width=820)
        if self.stage==3:
            self._lesson_textbox(stage['body'],297,306,793,102,'normal')
            self._lesson_diagram(lesson)
            self._button('NEXT HOP' if self.diagram_hop<len(lesson.diagram)-1 else 'REPLAY FLOW',284,538,199,35,
                         self._advance_diagram)
            self._write(f'{self.diagram_hop+1}/{len(lesson.diagram)} path nodes',506,544,'small',MUTED)
        elif self.stage==6:
            self._lesson_textbox(stage['body'],299,306,790,95,'normal')
            for i,answer in enumerate(m.assessment['choices']):
                self._button(f'{i+1}. {answer}',294,410+i*46,802,40,lambda i=i:self._practice_answer(i))
            if self.practice_feedback:
                self._write(self.practice_feedback,295,554,'small',GOOD if self.practice_ok else BAD,max_width=785,max_lines=2)
        elif self.stage==7:
            self._lesson_textbox(stage['body'],297,302,793,146,'normal')
            self._rect(289,456,803,57,CARD,7,ACCENT)
            self._write(('> '+self.field_note[-104:]+'▌') if self.field_note else 'Click here and type a short observation + uncertainty…',
                        303,472,'small',TEXT if self.field_note else MUTED,max_width=760,max_lines=2)
            self.buttons.append((self.pg.Rect(289,456,803,57),lambda:self._focus_note()))
            self._write(self.error or f'{len(self.field_note)}/1200 characters · self-reflection, not graded evidence',299,519,'small',BAD if self.error else MUTED)
            self._button('SAVE FIELD NOTE',296,546,244,34,self._save_field_note,highlight=True)
        else:
            self._lesson_textbox(stage['body'],297,307,793,233,'normal')
        if self.stage not in (6,7):
            self._write(stage['action'],294,550,'small',MUTED,max_width=801,max_lines=1)
        if self.stage>0:self._button('◀ PREVIOUS',288,591,180,39,lambda:self._go_stage(self.stage-1))
        if self.stage not in (6,7,3) and self.stage not in done:
            self._button('MARK STAGE COMPLETE',483,591,277,39,self._complete_stage,highlight=True)
        elif self.stage==3 and self.diagram_hop==len(lesson.diagram)-1 and 3 not in done:
            self._button('RECORD FLOW REVIEW',483,591,277,39,self._complete_stage,highlight=True)
        if self.stage<8:self._button('NEXT STAGE ▶',776,591,160,39,lambda:self._go_stage(self.stage+1))
        else:self._button('MISSION ASSESSMENT',757,591,208,39,lambda:self.navigate('assessment'),highlight=True)
        self._button('MISSIONS',984,591,111,39,lambda:self.navigate('missions'))

    def _advance_diagram(self):
        nodes=self.lessons.get(self.mid).diagram
        self.diagram_hop=(self.diagram_hop+1)%len(nodes)

    def _focus_note(self):
        self.focus='field_note'

    def _save_field_note(self):
        self._complete_stage(7)

    def draw_assessment(self):
        m=self.curriculum.get(self.mid);a=m.assessment
        self._panel(f'{m.id} — KNOWLEDGE CHECK','Answers give feedback. Real lab completion and actual competence are tracked separately.')
        if m.id in LAB_MISSIONS:
            kind=LAB_MISSIONS[m.id]
            r=self.session.lab_results.get(m.id)
            self._button(f'RUN CONTROLLED {kind.upper()} LAB',292,201,348,45,lambda kind=kind:self._run_mission_lab(kind),highlight=True)
            if r:
                self._write(f'LAB RESULT: {r.mode.upper()} / {"PASS" if r.success else "FAILED"}',675,203,'small',GOOD if r.success else BAD)
                self._write(' | '.join(r.details[:2]),675,226,'small',MUTED,max_width=435,max_lines=2)
            else:self._write('Lab must be run before submitting this assessment.',672,205,'small',GOLD,max_width=410,max_lines=2)
            q_y=285;button_y=379
        else:
            self._write('GUIDED REVIEW',295,207,'small',GOLD)
            self._write(a['objective'],295,236,'normal',MUTED,max_width=770,max_lines=2)
            q_y=307;button_y=412
        self._write(a['question'],295,q_y,'medium',TEXT,max_width=790,max_lines=3,line_height=31)
        for i,choice in enumerate(a['choices']):
            self._button(f'{i+1}. {choice}',292,button_y+i*51,811,44,lambda i=i:self._answer(i),enabled=not self.correct,highlight=self.selected_answer==i)
        if self.feedback:self._write(self.feedback,293,565,'small',GOOD if self.correct else BAD,max_width=810,max_lines=2,line_height=22)
        if self.correct:
            self._button('NEXT MISSION',845,608,256,31,self._next_mission,highlight=True)
        else:
            self._button('BACK TO LESSON',291,608,213,31,lambda:self.navigate('lesson'))

    def _run_mission_lab(self,kind):
        self.notice='';self.error=''
        # User-triggered only; update window before a possible short blocking subprocess.
        self._write('Running controlled lab…',700,205,'small',GOLD)
        size=self.screen.get_size()
        if size==(WIDTH,HEIGHT):self.screen.blit(self.canvas,(0,0))
        else:self.pg.transform.smoothscale(self.canvas,size,self.screen)
        self.pg.display.flip()
        try:
            result=run_lab(kind)
            self.session.attach_lab(self.mid,result)
            self.notice=f'{result.title}: {result.mode}, {"pass" if result.success else "failed"}. Details in Tool Labs.'
        except (OSError,ValueError) as exc:self.error=f'Lab error: {exc}'

    def _answer(self,index):
        if self.correct:return
        self.selected_answer=index
        good,feedback=self.session.submit(self.mid,index)
        self.correct=good;self.feedback=feedback

    def _next_mission(self):
        chapter=int(self.mid[2:4]);index=int(self.mid[-2:])
        if index<10:self.open_mission(f'CH{chapter:02d}-M{index+1:02d}')
        elif chapter<10:self.chapter=chapter+1;self.page='story'
        else:self.page='ending'

    def draw_operator_room(self):
        """Playable animation sandbox: move the selected operator with WASD/arrows."""
        self._panel('MERIDIAN // OPERATIONS FLOOR',
                    'Move using WASD or arrow keys. This is a fictional training floor, not an online world.')
        pg=self.pg
        # One room, deterministic layout, no external assets or network activity.
        self._rect(281,205,833,386,(11,29,44),12)
        self._rect(295,219,801,131,(17,44,59),4)
        for i in range(5):
            x=322+i*147
            self._rect(x,237,121,78,(22,50,70),5)
            self._rect(x+12,247,97,53,(7,20,31),4,border=ACCENT if i==2 else BORDER)
            self._write(('NEXUS','DNS','MIRROR-07','GATEWAY','ARCHIVE')[i],x+16,264,'small',ACCENT if i==2 else MUTED,max_width=95,max_lines=1)
        self._rect(295,360,801,226,(29,49,61),6)
        for xx in range(314,1080,64):
            pg.draw.line(self.canvas,(34,59,68),(xx,360),(xx,585),1)
        for yy in (406,464,520,580):
            pg.draw.line(self.canvas,(38,66,75),(295,yy),(1094,yy),1)
        # Scene props, kept clear of the player walkable zone.
        self._rect(323,368,187,34,(66,80,83),6)
        self._write('CASE TERMINAL',337,377,'small',TEXT,max_width=165)
        self._rect(899,370,174,32,(65,70,72),6)
        self._write('AUTHORIZED LAB',911,378,'small',TEXT,max_width=150)
        if self.session:
            profile=self.store.player(self.profile_id)
            draw_operator(pg,self.canvas,self.room_x,self.room_y,profile['appearance'],pg.time.get_ticks(),
                          moving=self.room_moving,facing=self.room_facing,scale=1.0,
                          reduced_motion=self.reduced_motion)
            self._write(profile['codename'],int(self.room_x)-35,int(self.room_y)-194,'small',ACCENT,max_width=100,max_lines=1)
        self._write('IDLE: blink / breathe     MOVE: walk     Press M to toggle motion reduction',300,611,'small',MUTED,max_width=790,max_lines=1)
        self._button('STORY',881,602,110,37,lambda:self.navigate('story'))
        self._button('HOME',999,602,110,37,lambda:self.navigate('home'))

    def update(self,dt):
        """Frame-rate independent character movement, never acts on real devices."""
        if self.page=='cinematic':
            self.cutscene.tick(dt)
        if self.page=='journey':
            self.journey.tick(dt)
        self.room_moving=False
        if self.page!='operator_room' or self.session is None:return
        keys=self.pg.key.get_pressed()
        dx=int(keys[self.pg.K_d] or keys[self.pg.K_RIGHT])-int(keys[self.pg.K_a] or keys[self.pg.K_LEFT])
        dy=int(keys[self.pg.K_s] or keys[self.pg.K_DOWN])-int(keys[self.pg.K_w] or keys[self.pg.K_UP])
        self.room_moving=bool(dx or dy)
        if dx:self.room_facing=1 if dx>0 else -1
        self.room_x,self.room_y=advance_position(self.room_x,self.room_y,dx,dy,dt)

    def draw_terminal(self):
        self._panel('SIMULATED TERMINAL / NEVER YOUR REAL SHELL','pwd · ls · cd · cat · ip · ping · traceroute · dig · help · clear')
        self._rect(285,201,815,358,(6,20,31),8)
        for i,line in enumerate(self.term_lines[-11:]):
            self._write(line,304,211+i*30,'small',ACCENT if line.startswith('>') else TEXT,max_width=774,max_lines=1)
        self._rect(286,574,810,49,CARD,7,ACCENT)
        self._write('> '+self.command+'▌',303,587,'normal',GOOD,max_width=770,max_lines=1)
        self._write('Type a simulation command and press Enter; no real commands are executed.',290,630,'small',MUTED,max_width=810)

    def draw_network(self):
        self._panel('SIMULATED NETWORK TOPOLOGY','Example topology. Click a device to inspect its address. No live network requests.')
        points={'workstation-07':(360,324),'switch-01':(548,324),'gateway':(734,324),'fileserver':(946,247),'dns':(946,406)}
        links=[('workstation-07','switch-01'),('switch-01','gateway'),('gateway','fileserver'),('gateway','dns')]
        for a,b in links:self.pg.draw.line(self.canvas,ACCENT,points[a],points[b],3)
        for name,(x,y) in points.items():
            fill=ACCENT if self.node==name else CARD
            self.pg.draw.circle(self.canvas,fill,(x,y),45)
            self.pg.draw.circle(self.canvas,BORDER,(x,y),45,2)
            fontcolor=BG if name==self.node else TEXT
            self._write(name[:11],x-42,y-7,'small',fontcolor,max_width=85,max_lines=1)
            self.buttons.append((self.pg.Rect(x-47,y-47,94,94),lambda n=name:self._set_node(n)))
        self._rect(300,503,792,104,CARD)
        self._write(f'SELECTED: {self.node.upper()}    IPv4 {HOSTS[self.node]}',319,516,'medium',GOOD,max_width=730)
        test_path=route(gateway_online=self.gateway_online)
        self._write('ROUTE: '+' → '.join(test_path),320,548,'small',GOOD if self.gateway_online else BAD,max_width=735,max_lines=2)
        self._button('SIMULATE GATEWAY FAILURE / RESTORE',317,572,425,29,self._toggle_gateway)
        self._button('PACKET JOURNEY',769,572,299,29,self._start_journey)

    def _toggle_gateway(self):
        self.gateway_online=not self.gateway_online

    def _set_node(self,name):self.node=name

    def draw_evidence(self):
        self._panel('CASE BOARD // EVIDENCE INTEGRITY','Observations are not automatically proof of intent.')
        notes=self.store.evidence(self.profile_id) if self.session else []
        if not notes:self._write('No case evidence collected yet. Complete chapter-ending missions.',295,240,'normal',MUTED,max_width=780)
        for i,(code,desc) in enumerate(notes[:10]):
            y=201+i*37
            self._write(code.upper().replace('_',' '),292,y,'small',GOLD,max_width=230,max_lines=1)
            self._write(desc,524,y,'small',TEXT,max_width=576,max_lines=1)
        self._button('EXPORT TRAINING DOSSIER',293,585,349,42,self._export_dossier,highlight=True)
        self._button('CHAPTER CASE FILE',653,585,252,42,self._start_case)
        self._write('Synthetic artifacts only. No real person or organization is implicated.',656,593,'small',MUTED,max_width=450,max_lines=2)

    def _export_dossier(self):
        try:
            from nulltrace.investigations.report import export_dossier
            saved=export_dossier(self.store,self.profile_id)
            self.notice=f'Dossier saved: {saved}'
        except (OSError,ValueError) as exc:self.error=f'Export failed: {exc}'

    def draw_tools(self):
        self._panel('CONTROLLED TOOL LABORATORIES','Run only with explicit consent. Real web/Burp exercise requires a second terminal.')
        descriptions=[
            ('packet','TSHARK / OFFLINE PCAP','Three synthetic DNS frames from the bundled capture.'),
            ('nmap','NMAP / LOOPBACK','Temporary 127.0.0.1 TCP listener. No LAN scan.'),
            ('john','JOHN / SYNTHETIC HASH','Small local dictionary; generated training hash.'),
            ('web','BURP / LOCAL WEB PORTAL','Start: python -m nulltrace --web-lab. Then perform manual HTTP request.'),
            ('incident','NEXUS / EVIDENCE DOSSIER','Offline event timeline and integrity comparison.')]
        for i,(kind,title,desc) in enumerate(descriptions):
            y=201+i*83
            self._rect(289,y,815,76,CARD)
            self._write(title,307,y+9,'normal',TEXT)
            self._write(desc,308,y+43,'small',MUTED,max_width=575,max_lines=1)
            self._button('VERIFY LAB',880,y+17,206,40,lambda kind=kind:self._run_tool_preview(kind),highlight=i==3)
        self._write('Web receipt verifies a loopback HTTP request, not the client application used.',296,616,'small',GOLD,max_width=795)

    def _run_tool_preview(self,kind):
        self.page='tool_result'
        try:self.preview_result=run_lab(kind)
        except (ValueError,OSError) as exc:
            from nulltrace.labs.practical import LabResult
            self.preview_result=LabResult(False,'unavailable','Error',(str(exc),))

    def draw_tool_result(self):
        r=self.preview_result
        self._panel(r.title,'PREVIEW RUN · does not automatically complete a mission.')
        self._write(f'STATUS: {"PASS" if r.success else "ERROR"}   MODE: {r.mode.upper()}',299,214,'medium',GOOD if r.success else BAD)
        for i,line in enumerate(r.details[:9]):
            self._write('• '+line,302,266+i*37,'normal',TEXT,max_width=760,max_lines=2)
        self._button('RETURN TO LABS',301,583,340,49,lambda:self.navigate('tools'),highlight=True)

    def _record_disclosure(self, route):
        if route not in ('oversight','broad','restricted'):
            raise ValueError('Invalid disclosure route')
        if self.qa:self.qa_story_choices['disclosure_route']=route
        else:self.store.set_choice(self.profile_id,'disclosure_route',route)
        self.notice='Disclosure route recorded. Complete Chapter 10 to see your ending.'

    def draw_disclosure(self):
        self._panel('NEXUS PROTOCOL // DISCLOSURE DECISION',
                    'A story choice: no live credentials, networks, or third-party data are disclosed.')
        opts=[
            ('INDEPENDENT OVERSIGHT','oversight','Submit a preserved, minimized dossier for review.'),
            ('BROAD PUBLIC RELEASE','broad','Expose the programme publicly, risking unnecessary harm.'),
            ('RESTRICTED REVIEW','restricted','Contain the incident but leave accountability uncertain.')]
        choices=self.qa_story_choices if self.qa else self.store.choices(self.profile_id)
        for i,(label,route,explanation) in enumerate(opts):
            y=207+i*111
            self._rect(288,y,811,100,CARD)
            self._write(explanation,306,y+15,'normal',TEXT,max_width=775,max_lines=2)
            self._button(label,307,y+54,399,40,lambda r=route:self._record_disclosure(r),highlight=choices.get('disclosure_route')==route)
        self._write('Recorded: '+choices.get('disclosure_route','none'),307,557,'small',GOLD)
        self._button('RETURN TO CHAPTER 10',306,585,368,42,lambda:self.navigate('story'))

    def draw_ending(self):
        self._panel('NULLTRACE // FINAL CASE CONCLUSION','Your choices affect the story. All endings are fictional.')
        if not self.session or 'CH10-M10' not in self.session.completed and not self.qa:
            self._write('Complete CH10-M10 to unlock the final scene.',290,238,'medium',GOLD,max_width=790)
            self._button('RETURN TO MISSIONS',296,530,340,48,lambda:self.navigate('chapters'),highlight=True)
            return
        choices=self.qa_story_choices if self.qa else self.store.choices(self.profile_id)
        evidence={code for code,_ in self.store.evidence(self.profile_id)}
        ending=resolve_ending(choices,evidence)
        self._write(ending.title,293,218,'large',ACCENT)
        self._write(ending.summary,296,300,'medium',TEXT,max_width=782,max_lines=4,line_height=34)
        self._write(ending.epilogue,298,424,'normal',MUTED,max_width=767,max_lines=4,line_height=30)
        self._write(f'CASE EVIDENCE: {ending.evidence_count}/10 chapter summaries • Story route: {choices.get("disclosure_route", "restricted")}',296,518,'small',GOLD,max_width=794)
        self._button('VIEW EVIDENCE',295,562,290,52,lambda:self.navigate('evidence'),highlight=True)
        self._button('REPLAY CHAPTERS',610,562,290,52,lambda:self.navigate('chapters'))

    def handle(self,event):
        pg=self.pg
        if event.type == pg.QUIT:self.running=False;return
        if event.type == pg.KEYDOWN:
            if event.key==pg.K_ESCAPE:
                self.page='home' if self.page in ('chapters','profile','tools','story','terminal','network','evidence','tool_result','operator_room','disclosure','ending','academy','cinematic','casework','journey') else 'chapters'
                return
            if self.page=='lesson':
                if event.key==pg.K_PAGEUP:
                    self.lesson_scroll=max(0,self.lesson_scroll-170);return
                if event.key==pg.K_PAGEDOWN:
                    self.lesson_scroll+=170;return
                if self.stage==6 and event.key in (pg.K_1,pg.K_2,pg.K_3):
                    self._practice_answer(event.key-pg.K_1);return
                if self.stage==7 and event.key in (pg.K_RETURN,pg.K_KP_ENTER):
                    self._save_field_note();return
            if self.page=='cinematic':
                if event.key==pg.K_SPACE:self.cutscene.advance();return
                if event.key==pg.K_r:self.cutscene.restart();return
                if event.key==pg.K_m:
                    self.reduced_motion=not self.reduced_motion
                    if self.reduced_motion:self.cutscene.playing=False
                    return
            if self.page=='journey':
                if event.key==pg.K_SPACE:self.journey.step();return
                if event.key==pg.K_r:self.journey.reset();return
            if self.page=='operator_room' and event.key==pg.K_m:
                self.reduced_motion=not self.reduced_motion
                return
            if self.page=='profile':
                if event.key==pg.K_TAB:self.focus='codename' if self.focus=='name' else 'name';return
                if event.key==pg.K_BACKSPACE:
                    v=getattr(self,self.focus);setattr(self,self.focus,v[:-1]);return
                if event.key in (pg.K_RETURN,pg.K_KP_ENTER):self.new_profile();return
            if self.page=='terminal':
                if event.key==pg.K_BACKSPACE:self.command=self.command[:-1];return
                if event.key in (pg.K_RETURN,pg.K_KP_ENTER):
                    command=self.command.strip();self.command=''
                    result=self.terminal.execute(command)
                    if result=='\f':self.term_lines=[]
                    elif command:
                        self.term_lines.append('> '+command)
                        self.term_lines.extend(result.splitlines() or [''])
                        self.term_lines=self.term_lines[-50:]
                    return
            if self.page=='assessment' and event.key in (pg.K_1,pg.K_2,pg.K_3):self._answer(event.key-pg.K_1);return
        if event.type==pg.TEXTINPUT:
            if self.page=='profile':
                value=getattr(self,self.focus)
                if len(value)<32 and all(ord(ch)>=32 for ch in event.text):setattr(self,self.focus,(value+event.text)[:32])
            if self.page=='lesson' and self.stage==7 and len(self.field_note)<1200 and all(ord(ch)>=32 for ch in event.text):
                self.field_note=(self.field_note+event.text)[:1200]
            if self.page=='terminal' and len(self.command)<160 and all(ord(ch)>=32 for ch in event.text):self.command=(self.command+event.text)[:160]
        if event.type==pg.MOUSEWHEEL and self.page=='lesson':
            self.lesson_scroll=max(0,self.lesson_scroll-event.y*57)
        if event.type==pg.MOUSEBUTTONDOWN and event.button==1:
            w,h=self.screen.get_size();mx=int(event.pos[0]*WIDTH/w);my=int(event.pos[1]*HEIGHT/h)
            for r,action in reversed(self.buttons):
                if r.collidepoint(mx,my):action();break

    def loop(self,frames=None):
        clock=self.pg.time.Clock();counter=0
        while self.running:
            dt=min(clock.tick(30)/1000.0,0.05)
            for e in self.pg.event.get():self.handle(e)
            self.update(dt)
            self.render()
            counter+=1
            if frames is not None and counter>=frames:break

def run_game(qa=False)->int:
    try:import pygame
    except ImportError:
        print('Pygame is missing. Run bash scripts/setup_ubuntu.sh, then source .venv/bin/activate.')
        return 1
    game=None
    try:
        game=Game(pygame,qa=qa)
        game.loop()
        return 0
    finally:
        if game:game.close()
        else:pygame.quit()

def smoke_test()->int:
    try:import pygame
    except ImportError:
        print('Pygame is unavailable: cannot verify the game window in this environment.')
        return 1
    game=None
    try:
        game=Game(pygame)
        game.loop(frames=3)
        print('NULLTRACE Pygame UI smoke: PASS (3 frames).')
        return 0
    finally:
        if game:game.close()
        else:pygame.quit()
