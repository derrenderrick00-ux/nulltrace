"""v0.6.1 hotfix invariants: pcap streaming, minimal John, animated operator."""
from pathlib import Path
from unittest.mock import patch
import math
import subprocess

from nulltrace.labs.practical import packet_lab, john_lab, PCAP, TEST_PASSWORD
from nulltrace.ui.operator_animation import APPEARANCES, advance_position, frame_at


def test_packet_uses_stdin_and_never_opens_device():
    def fake_run(args, **kw):
        assert args[1:4] == ['-n', '-r', '-']
        assert not any(x in args for x in ('-i','-w'))
        assert isinstance(kw['input'], bytes)
        assert kw['input']==PCAP.read_bytes()
        assert not kw.get('text')
        return subprocess.CompletedProcess(args,0,
            b'192.0.2.10\t198.51.100.53\tmirror.training.invalid\n',b'')
    with patch('nulltrace.labs.practical.shutil.which',return_value='/usr/bin/tshark'), \
         patch('nulltrace.labs.practical.subprocess.run',side_effect=fake_run):
        result=packet_lab()
    assert result.success and result.mode=='real'
    assert 'stdin' in ' '.join(result.details)


def test_packet_does_not_claim_real_when_parser_returns_unrelated_traffic():
    with patch('nulltrace.labs.practical.shutil.which',return_value='/usr/bin/tshark'), \
         patch('nulltrace.labs.practical.subprocess.run',return_value=subprocess.CompletedProcess([],0,b'203.0.113.99\t198.51.100.53\tnot-the-training-name.invalid\n',b'')):
        result=packet_lab()
    assert result.mode=='simulated'


def test_minimal_john_uses_its_temp_home_and_no_jumbo_only_options():
    visited=[]
    def fake_run(args, **kw):
        if 'openssl' in args[0]:
            return subprocess.CompletedProcess(args,0,'$1$ntlab$generatedTrainingHash\n','')
        assert 'john' in args[0]
        assert all(not arg.startswith('--pot') for arg in args)
        assert kw['cwd']==Path(kw['env']['HOME'])
        assert Path(kw['env']['HOME']).exists()
        assert Path(kw['cwd'],'synthetic.hash').exists()
        assert Path(kw['cwd'],'wordlist.txt').exists()
        visited.append(Path(kw['cwd']))
        if '--show' in args:
            return subprocess.CompletedProcess(args,0,f'training:{TEST_PASSWORD}\n1 password hash cracked\n','')
        return subprocess.CompletedProcess(args,0,'','Loaded 1 password hash')
    def which(cmd):return f'/usr/bin/{cmd}'
    with patch('nulltrace.labs.practical.shutil.which',side_effect=which), \
         patch('nulltrace.labs.practical.subprocess.run',side_effect=fake_run):
        result=john_lab()
    assert result.success and result.mode=='real'
    assert len(visited)==2 and visited[0]==visited[1]
    assert not visited[0].exists()  # TemporaryDirectory cleaned after lab


def test_minimal_john_failure_does_not_mislabel_simulation():
    def fake_run(args, **kw):
        if 'openssl' in args[0]:
            return subprocess.CompletedProcess(args,0,'$1$ntlab$fixture\n','')
        return subprocess.CompletedProcess(args,2,'','Unknown option --format')
    with patch('nulltrace.labs.practical.shutil.which',side_effect=lambda x:f'/usr/bin/{x}'), \
         patch('nulltrace.labs.practical.subprocess.run',side_effect=fake_run):
        result=john_lab()
    assert result.success and result.mode=='simulated'


def test_animation_idle_blinks_and_breathes():
    early=frame_at(60)
    assert early.blink
    normal=frame_at(600)
    assert not normal.blink
    assert normal.bob!=frame_at(1200).bob
    assert all(-2<=frame_at(t).bob<=2 for t in range(0,5000,20))


def test_animation_walk_has_stride_but_reduced_motion_disables():
    walking=frame_at(150,True)
    assert abs(walking.leg_swing)>0
    assert abs(walking.arm_swing)>0
    reduced=frame_at(150,True,True)
    assert reduced.bob==reduced.leg_swing==reduced.arm_swing==0
    assert not reduced.blink


def test_walk_is_normalized_and_clamped():
    x,y=advance_position(600,450,1,1,0.05)
    assert math.isclose(math.hypot(x-600,y-450),8.5,abs_tol=.001)
    assert advance_position(1044,559,1,1,1)==(1044,559)
    assert advance_position(344,400,-1,-1,1)==(344,400)
    assert advance_position(600,450,0,0,1)==(600,450)


def test_supported_outfits_stable():
    assert APPEARANCES == ('hoodie','analyst','technician')
