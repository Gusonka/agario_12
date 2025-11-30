from math import hypot
from socket import socket, AF_INET, SOCK_STREAM
from pygame import *
from threading import Thread
from random import randint
from launcher import ConnectWindow


win = ConnectWindow()
win.mainloop()

name = win.name
port = win.port
host = win.host

sock = socket(AF_INET, SOCK_STREAM)
sock.connect((host, port))

my_data = list(map(int, sock.recv(64).decode().strip().split(',')))
my_id = my_data[0]
my_player = my_data[1:]
sock.setblocking(False)


init()
window = display.set_mode((1000, 1000))
display.set_caption("Їж кульки – стань найбільшим!")
clock = time.Clock()

big_font = font.Font(None, 50)
name_font = font.Font(None, 28)
win_font = font.Font(None, 120)

all_players = []
running = True
lose = False
win_game = False


def receive_data():
    global all_players, running, lose, win_game
    while running:
        try:
            data = sock.recv(4096).decode().strip()
            if not data:
                continue

            if data == "LOSE":
                lose = True
            elif data == "WIN":
                win_game = True
            else:
                parts = data.strip('|').split('|')
                new_list = []
                for p in parts:
                    ps = p.split(',')
                    if len(ps) >= 5:
                        player_id = int(ps[0])
                        x, y, r = map(int, ps[1:4])
                        player_name = ps[4]
                        new_list.append([player_id, x, y, r, player_name])
                all_players = new_list
        except:
            pass

Thread(target=receive_data, daemon=True).start()


class Eat:
    def __init__(self, x, y, r, c):
        self.x = x
        self.y = y
        self.radius = r
        self.color = c

    def check_collision(self, player_x, player_y, player_r):
        return hypot(self.x - player_x, self.y - player_y) <= self.radius + player_r

eats = [
    Eat(randint(-2000, 2000), randint(-2000, 2000), 10,
        (randint(50, 255), randint(50, 255), randint(50, 255)))
    for _ in range(300)
]


while running:
    for e in event.get():
        if e.type == QUIT:
            running = False

    window.fill((30, 30, 40))


    if lose:
        txt = big_font.render('Ти програв!', True, (255, 50, 50))
        window.blit(txt, (500 - txt.get_width()//2, 450))
        display.update()
        clock.tick(60)
        continue


    if len(eats) == 0 or win_game:
        win_game = True
        txt = win_font.render('ТИ ПЕРЕМІГ!', True, (0, 255, 100))
        window.blit(txt, (500 - txt.get_width()//2, 350))
        sub = big_font.render('Ти з’їв усі 300 кульок!', True, (255, 255, 255))
        window.blit(sub, (500 - sub.get_width()//2, 480))
        display.update()
        clock.tick(60)
        continue


    scale = max(0.3, min(50 / my_player[2], 1.5))


    for p in all_players:
        if p[0] == my_id:
            continue
        sx = int((p[1] - my_player[0]) * scale + 500)
        sy = int((p[2] - my_player[1]) * scale + 500)
        rad = int(p[3] * scale)

        draw.circle(window, (255, 100, 100), (sx, sy), rad)
        name_txt = name_font.render(p[4], True, (255, 255, 255))
        window.blit(name_txt, (sx - name_txt.get_width()//2, sy - rad - 25))


    my_rad_scaled = int(my_player[2] * scale)
    draw.circle(window, (50, 255, 50), (500, 500), my_rad_scaled)
    my_name_txt = name_font.render(name, True, (255, 255, 255))
    window.blit(my_name_txt, (500 - my_name_txt.get_width()//2, 500 - my_rad_scaled - 25))


    to_remove = []
    for eat in eats:
        if eat.check_collision(my_player[0], my_player[1], my_player[2]):
            to_remove.append(eat)
            my_player[2] += int(eat.radius * 0.2)
        else:
            ex = int((eat.x - my_player[0]) * scale + 500)
            ey = int((eat.y - my_player[1]) * scale + 500)
            draw.circle(window, eat.color, (ex, ey), int(eat.radius * scale))

    for eat in to_remove:
        eats.remove(eat)


    counter = big_font.render(f"З'їдено: {300 - len(eats)} / 300", True, (255, 255, 100))
    window.blit(counter, (10, 10))

    display.update()
    clock.tick(60)


    if not lose and not win_game:
        keys = key.get_pressed()
        speed = 15
        if keys[K_w]:
            my_player[1] -= speed
        if keys[K_s]:
            my_player[1] += speed
        if keys[K_a]:
            my_player[0] -= speed
        if keys[K_d]:
            my_player[0] += speed

        try:
            msg = f"{my_id},{my_player[0]},{my_player[1]},{my_player[2]},{name}"
            sock.send(msg.encode())
        except:
            pass

quit()