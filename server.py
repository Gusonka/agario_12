
import pygame
from pygame import *
import socket
from threading import Thread
from random import randint, choice
from launcher import ConnectWindow


win = ConnectWindow()
win.mainloop()

name = win.name.strip() or "Гравець"
host = win.host
port = int(win.port)

sock = socket.socket()
sock.connect((host, port))


data = sock.recv(1024).decode()
my_id, x, y, r = map(int, data.split(','))
my_x, my_y, my_r = x, y, r


pygame.init()
screen = display.set_mode((1000, 1000))
display.set_caption("Їж кульки – стань найбільшим!")
clock = time.Clock()
font1 = font.Font(None, 50)
font2 = font.Font(None, 30)


colors = [(255,99,99), (99,255,99), (99,99,255), (255,255,99), (255,99,255), (99,255,255)]
my_color = colors[0]
eaten = 0


foods = []
for i in range(300):
    foods.append([
        randint(-2000, 2000),
        randint(-2000, 2000),
        (randint(100,255), randint(100,255), randint(100,255))
    ])

running = True
lose = False
win_game = False

def get_players():
    global lose, win_game
    sock.setblocking(False)
    while running:
        try:
            msg = sock.recv(4096).decode()
            if msg == "LOSE":
                lose = True
            elif msg == "WIN":
                win_game = True
            else:

                pass
        except:
            pass

Thread(target=get_players, daemon=True).start()
while running:
    for e in event.get():
        if e.type == QUIT:
            running = False

    screen.fill((20, 20, 40))


    mx, my = mouse.get_pos()
    dx = mx - 500
    dy = my - 500
    if abs(dx) + abs(dy) > 10:
        speed = max(3, 8 - my_r // 20)
        my_x += dx * speed * 0.01
        my_y += dy * speed * 0.01


    zoom = max(0.2, 60 / my_r)


    new_foods = []
    for fx, fy, color in foods:
        sx = (fx - my_x) * zoom + 500
        sy = (fy - my_y) * zoom + 500


        if (fx - my_x)**2 + (fy - my_y)**2 <= (my_r + 10)**2:
            my_r += 2
            eaten += 1
            if eaten % 10 == 0:
                my_color = choice(colors)
        else:
            draw.circle(screen, color, (int(sx), int(sy)), int(10 * zoom))
            new_foods.append([fx, fy, color])
    foods = new_foods


    draw.circle(screen, (0,0,0), (500, 500), my_r * zoom + 10)  # тінь
    draw.circle(screen, my_color, (500, 500), int(my_r * zoom))
    draw.circle(screen, (255,255,255), (500, 500), int(my_r * zoom), 5)

    txt = font2.render(name, True, (255,255,255))
    screen.blit(txt, (500 - txt.get_width()//2, 500 - my_r * zoom - 40))


    info = font1.render(f"З'їдено: {eaten} / 300", True, (255, 255, 100))
    screen.blit(info, (20, 20))


    if eaten >= 300:
        win_text = font1.render("ТИ ПЕРЕМІГ!!!", True, (0, 255, 0))
        screen.blit(win_text, (500 - win_text.get_width()//2, 450))


    try:
        msg = f"{my_id},{int(my_x)},{int(my_y)},{my_r},{name}"
        sock.send(msg.encode())
    except:
        pass

    display.update()
    clock.tick(60)

sock.close()
pygame.quit()
