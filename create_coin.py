import pygame

pygame.init()


coin = pygame.Surface((14, 14), pygame.SRCALPHA)


pygame.draw.circle(coin, (255, 215, 0), (7, 7), 6)
pygame.draw.circle(coin, (255, 255, 100), (5, 5), 2)  # блик
pygame.draw.circle(coin, (180, 150, 0), (7, 7), 6, 1)  # обводка

pygame.image.save(coin, "images/coin.png")
print("coin.png создана!")