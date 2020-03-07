import wiiboard
import pygame
import time
import datetime


def main():
    board = wiiboard.Wiiboard()

    pygame.init()

    # address = board.discover()
    address = '00:26:59:7B:7F:5F'
    board.connect(address)  # The wii board must be in sync mode at this time

    time.sleep(0.1)
    board.setLight(True)
    done = False
    width = 1300
    height = 900

    date_format = '%Y-%m-%d %H:%M:%S.%f'
    black = (0, 0, 0)
    white = (255, 255, 255)

    screen = pygame.display.set_mode((width, height))

    # log
    pos_log = []

    # step counter
    step_log = []
    step_count = 0
    last_step = None
    font = pygame.font.Font(None, 120)

    with open('var/log-{}.txt'.format(datetime.datetime.now().strftime('%Y%m%d%H%M%S')), 'w') as f:
        while (not done):
            time.sleep(0.05)
            for event in pygame.event.get():
                if event.type == wiiboard.WIIBOARD_MASS:
                    # 10KG. otherwise you would get alot of useless small events!
                    if (event.mass.totalWeight > 10):
                        # write log
                        dt_now = datetime.datetime.now()
                        now = dt_now.strftime(date_format)
                        f.write('{},{},{},{},{},{}\n'.format(
                            now,
                            event.mass.topLeft,
                            event.mass.topRight,
                            event.mass.bottomLeft,
                            event.mass.bottomRight,
                            event.mass.totalWeight
                        ))

                        # step counter
                        mass_left = event.mass.topLeft + event.mass.bottomLeft
                        mass_right = event.mass.topRight + event.mass.bottomRight
                        step_log.append([mass_left, mass_right])
                        current_step = mass_left > mass_right
                        if last_step != current_step:
                            step_count += 1
                            print(str(step_count))
                        last_step = current_step

                        # calcurate center point
                        # print "--Mass event--   Total weight: " + `event.mass.totalWeight` + ". Top left: " + `event.mass.topLeft`
                        y = (event.mass.bottomLeft +
                             event.mass.bottomRight) / event.mass.totalWeight
                        x = (event.mass.topRight + event.mass.bottomRight) / \
                            event.mass.totalWeight
                        pos = tuple([int(d) for d in [x * width, y * height]])
                        pos_log.append(pos)

                        # delete log
                        if len(pos_log) > 5000:
                            pos_log = pos_log[-1000:]
                        if len(step_log) > 5000:
                            step_log = step_log[-1000:]

                        # update display
                        screen.fill(black)
                        # draw counter
                        text_stepcount = font.render(
                            str(step_count), True, white)
                        screen.blit(text_stepcount, (width - 150, 50))

                        # draw mass
                        sum_left = sum([x[0] for x in step_log[-800:]])
                        sum_right = sum([x[1] for x in step_log[-800:]])
                        sum_mass = sum_left + sum_right
                        text_left = font.render(
                            '{:0.1f}'.format(sum_left / sum_mass * 100), True, white)
                        screen.blit(text_left, (280, 700))

                        text_right = font.render(
                            '{:0.1f}'.format(sum_right / sum_mass * 100), True, white)
                        screen.blit(text_right, (820, 700))

                        # draw point
                        for pos in pos_log[-300:]:
                            pygame.draw.circle(screen, white + (128,), pos, 5)

                        # update frame
                        pygame.display.flip()
                # etc for topRight, bottomRight, bottomLeft. buttonPressed and buttonReleased also available but easier to use in seperate event

                elif event.type == wiiboard.WIIBOARD_BUTTON_PRESS:
                    print("Button pressed!")
                    screen.fill(black)
                    pygame.display.flip()
                    step_count = 0
                    last_step = None
                    pos_log = []
                    step_log = []
                    f.write('\n')

                elif event.type == wiiboard.WIIBOARD_BUTTON_RELEASE:
                    print("Button released")
                    # done = True

                # Other event types:
                # wiiboard.WIIBOARD_CONNECTED
                # wiiboard.WIIBOARD_DISCONNECTED

    board.disconnect()
    pygame.quit()


# Run the script if executed
if __name__ == "__main__":
    main()
