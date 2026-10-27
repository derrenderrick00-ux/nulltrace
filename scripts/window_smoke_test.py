"""Optional Phase 0 Pygame graphical check. NOT gameplay."""
import sys
import time

try:
    import pygame
except ImportError:
    print("pygame-ce is not installed. Run the setup script first.", file=sys.stderr)
    raise SystemExit(2)

pygame.init()
try:
    screen = pygame.display.set_mode((640, 320))
    pygame.display.set_caption("NULLTRACE — Phase 0 graphics check")
    clock = pygame.time.Clock()
    font = pygame.font.Font(None, 34)
    small = pygame.font.Font(None, 22)
    start = time.monotonic()
    active = True
    while active and time.monotonic() - start < 8:
        for event in pygame.event.get():
            if event.type == pygame.QUIT or (event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE):
                active = False
        screen.fill((19, 28, 38))
        screen.blit(font.render("NULLTRACE / GRAPHICS CHECK", True, (220, 235, 243)), (46, 104))
        screen.blit(small.render("Pygame is running. Press Esc or close this window.", True, (164, 197, 211)), (46, 158))
        pygame.display.flip()
        clock.tick(30)
    print("Pygame window check finished without an exception.")
finally:
    pygame.quit()
