import pygame as pg

def palette_swap(img, surf, old_c, new_c):
    img_copy = pg.Surface(img.get_size())
    img_copy.fill(new_c)
    surf.set_colorkey(old_c)
    img_copy.blit(surf, (0, 0))
    return img_copy

def blue_ebonheart(img):
    "Changes color of the image"
    img = palette_swap(img, img, (180, 32, 42), (17, 11, 96))
    img = palette_swap(img, img, (120, 23, 30), (83, 32, 145))
    img = palette_swap(img, img, (144, 25, 33), (167, 65, 131))
    # img = palette_swap(img, (154, 209, 59), (205, 124, 97))
    return img