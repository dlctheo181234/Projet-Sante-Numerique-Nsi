import numpy as np
import pygame

length, width = 960, 640                          # taille de la fenêtre (pixels)
tile_size = 4                                     # taille d'une case en pixels
W, H = length // tile_size, width // tile_size    # taille de la carte (cases)


class Map:
    # ---------------------------------------------------------------- params zones
    BIOMES = [
        # nom,                 couleur RGB
        ("zone résidentielle", (255, 0, 0)),
        ("zone commerciale",   (0, 255, 0)),
        ("rue",                (40, 40, 40)),
        ("parc",               (20, 110, 40)),
    ]
    PALETTE = np.array([c for _, c in BIOMES], dtype=np.uint8)
    RUE = 2

    def __init__(self, w=W, h=H, graine=42, ville=True, echelle=48.0):
        self.w, self.h = w, h
        self.graine, self.ville, self.echelle = graine, ville, echelle
        self.population = None   # tableau (h, w) entre 0 et 1
        self.biomes = None       # tableau (h, w) d'indices dans BIOMES
        self.image = None        # pygame.Surface prête à afficher
        self.generer()

    # ---------------------------------------------------------------- bruit
    @staticmethod
    def noise_value(w, h, scale, rng):
        """Grille de valeurs aléatoires interpolée en douceur."""
        scale = max(scale, 1.0)
        gw, gh = int(w / scale) + 2, int(h / scale) + 2
        grid = rng.random((gh, gw))

        xs = np.arange(w) / scale
        ys = np.arange(h) / scale
        x0, y0 = xs.astype(int), ys.astype(int)
        tx, ty = xs - x0, ys - y0
        # smoothstep : la transition entre deux points de la grille démarre et
        # finit en douceur (pente nulle), donc on ne voit pas de "cassure" aux
        # bords de chaque carré de la grille # pas compris
        tx = tx * tx * (3 - 2 * tx)
        ty = ty * ty * (3 - 2 * ty)

        a = grid[np.ix_(y0, x0)]
        b = grid[np.ix_(y0, x0 + 1)]
        c = grid[np.ix_(y0 + 1, x0)]
        d = grid[np.ix_(y0 + 1, x0 + 1)]
        TX, TY = tx[None, :], ty[:, None]
        haut = a + (b - a) * TX
        bas = c + (d - c) * TX
        return haut + (bas - haut) * TY

    @staticmethod
    def bruit_fractal(w, h, seed, scale:float=48.0, octaves=6, persistance=0.5):
        rng = np.random.default_rng(seed)
        total = np.zeros((h, w))
        amp, norme = 1.0, 0.0
        for _ in range(octaves):
            total += amp * Map.noise_value(w, h, scale, rng)
            norme += amp
            amp *= persistance
            scale /= 2
        return total / norme

    @staticmethod
    def masque_centre(w, h):
        y, x = np.mgrid[0:h, 0:w]
        dx = (x - w / 2) / (w / 2)
        dy = (y - h / 2) / (h / 2)
        return np.clip(np.sqrt(dx * dx + dy * dy), 0, 1)

    @staticmethod
    def normaliser(t):
        """Ramène un tableau entre 0 et 1."""
        return (t - t.min()) / (t.max() - t.min())

    # ---------------------------------------------------------------- zones
    @staticmethod
    def classer(population, density):
        """Type de Zone de chaque case selon le bruit"""
        conditions = [
            density < 0.25,          # peu dense -> parc
            population < 0.45,       # population moyenne -> résidentiel
        ]
        choix = [3, 0]
        return np.select(conditions, choix, default=1)   # le reste -> commercial

    # ---------------------------------------------------------------- rues
    def decouper(self, x, y, w, h, rng, profondeur, rues, blocs, taille_min=8):
        """Découpage récursif (BSP) : on coupe le rectangle en deux par une rue,
        puis on recommence sur chaque moitié jusqu'à obtenir des pâtés de maisons.""" #TROP SMART
        largeur_rue = 3 if profondeur < 2 else 1
        trop_petit = max(w, h) < 2 * taille_min + largeur_rue
        petit_bloc = max(w, h) < 4 * taille_min
        if trop_petit or (petit_bloc and rng.random() < 0.3):
            blocs.append((x, y, w, h))
            return

        if w >= h:
            c = int(rng.integers(x + taille_min, x + w - taille_min - largeur_rue + 1))
            rues[y:y + h, c:c + largeur_rue] = True
            self.decouper(x, y, c - x, h, rng, profondeur + 1, rues, blocs, taille_min)
            self.decouper(c + largeur_rue, y, x + w - c - largeur_rue, h, rng, profondeur + 1, rues, blocs, taille_min)
        else:
            c = int(rng.integers(y + taille_min, y + h - taille_min - largeur_rue + 1))
            rues[c:c + largeur_rue, x:x + w] = True
            self.decouper(x, y, w, c - y, rng, profondeur + 1, rues, blocs, taille_min)
            self.decouper(x, c + largeur_rue, w, y + h - c - largeur_rue, rng, profondeur + 1, rues, blocs, taille_min)

    # ---------------------------------------------------------------- génération
    def generer(self):
        '''génère la carte'''
        w, h = self.w, self.h
        rng = np.random.default_rng(self.graine)

        # 1. bruit de population (+ centre-ville si ville=True) et de densité
        pop = self.normaliser(self.bruit_fractal(w, h, self.graine, scale=self.echelle))
        if self.ville:
            pop = np.clip(pop - 0.65 * self.masque_centre(w, h) ** 2, 0, 1)
            pop = pop / pop.max()
        dens = self.normaliser(self.bruit_fractal(w, h, self.graine + 1000,
        scale=self.echelle * 1.5, octaves=4))
        zones = self.classer(pop, dens)

        # 2. réseau de rues procédural
        rues = np.zeros((h, w), dtype=bool)
        blocs = []
        self.decouper(0, 0, w, h, rng, 0, rues, blocs)

        # 3. chaque pâté prend une seule zone : celle du bruit en son centre
        biomes = np.empty((h, w), dtype=int)
        for (x, y, bw, bh) in blocs:
            biomes[y:y + bh, x:x + bw] = zones[y + bh // 2, x + bw // 2]
        biomes[rues] = self.RUE

        self.population, self.biomes = pop, biomes
        self.image = self.vers_surface()

    def vers_surface(self):
        rgb = self.PALETTE[self.biomes].astype(np.float32)
        rgb *= (0.75 + 0.35 * self.population)[..., None]
        rgb = np.clip(rgb, 0, 255).astype(np.uint8)
        surf = pygame.surfarray.make_surface(rgb.transpose(1, 0, 2))
        return pygame.transform.scale(surf, (self.w * tile_size, self.h * tile_size))

    def info_case(self, cx, cy):
        if 0 <= cx < self.w and 0 <= cy < self.h:
            nom = self.BIOMES[self.biomes[cy, cx]][0]
            return f"({cx},{cy})  population {self.population[cy, cx]:.2f}  {nom}"
        return ""


# ---------------------------------------------------------------- démo technique
def main():
    pygame.init()
    ecran = pygame.display.set_mode((length, width))
    police = pygame.font.SysFont(None, 24)
    horloge = pygame.time.Clock()

    carte = Map()
    info = ""
    en_cours = True
    while en_cours:
        regen = False
        for ev in pygame.event.get():
            if ev.type == pygame.QUIT:
                en_cours = False
            elif ev.type == pygame.KEYDOWN:
                if ev.key == pygame.K_ESCAPE:
                    en_cours = False
                elif ev.key == pygame.K_SPACE:
                    carte.graine = np.random.randint(0, 1_000_000); regen = True
                elif ev.key == pygame.K_i:
                    carte.ville = not carte.ville; regen = True
                elif ev.key in (pygame.K_PLUS, pygame.K_KP_PLUS, pygame.K_EQUALS):
                    carte.echelle *= 1.25; regen = True
                elif ev.key in (pygame.K_MINUS, pygame.K_KP_MINUS):
                    carte.echelle /= 1.25; regen = True
                elif ev.key == pygame.K_s:
                    pygame.image.save(carte.image, f"carte_{carte.graine}.png")
                    info = f"Sauvegardé : carte_{carte.graine}.png"
            elif ev.type == pygame.MOUSEWHEEL:          # molette = zoom du bruit
                carte.echelle *= 1.25 if ev.y > 0 else 1 / 1.25
                regen = True
            elif ev.type == pygame.MOUSEBUTTONDOWN and ev.button == 1:
                info = carte.info_case(ev.pos[0] // tile_size, ev.pos[1] // tile_size)

        if regen:
            carte.generer()
            info = ""

        ecran.blit(carte.image, (0, 0))
        texte = (f"graine {carte.graine} | {'ville' if carte.ville else 'quartier'} "
                 f"| échelle {carte.echelle:.0f}")
        for i, ligne in enumerate((texte, info)):
            if ligne:
                s = police.render(ligne, True, (255, 255, 255), (0, 0, 0))
                ecran.blit(s, (8, 8 + i * 24))
        pygame.display.flip()
        horloge.tick(30)
    pygame.quit()


if __name__ == "__main__":
    main()