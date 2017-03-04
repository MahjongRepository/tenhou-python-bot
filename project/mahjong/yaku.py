class Yaku(object):
    yaku_id = None
    name = ''
    han = {'open': None, 'closed': None}
    is_yakuman = False

    def __init__(self, yaku_id, name, open_value, closed_value, is_yakuman=False):
        self.id = yaku_id
        self.name = name
        self.han = {'open': open_value, 'closed': closed_value}
        self.is_yakuman = is_yakuman

    def __str__(self):
        if self.name == 'Dora' or self.name == 'Aka Dora':
            return '{} {}'.format(self.name, self.han['open'])
        else:
            return self.name

    # for calls in array
    def __repr__(self):
        return self.__str__()

# Yaku situations
tsumo = Yaku(0, 'Menzen Tsumo', None, 1)
riichi = Yaku(1, 'Riichi', None, 1)
ippatsu = Yaku(2, 'Ippatsu', None, 1)
chankan = Yaku(3, 'Chankan', 1, 1)
rinshan = Yaku(4, 'Rinshan Kaihou', 1, 1)
haitei = Yaku(5, 'Haitei Raoyue', 1, 1)
houtei = Yaku(6, 'Houtei Raoyui', 1, 1)
daburu_riichi = Yaku(21, 'Double Riichi', None, 2)
nagashi_mangan = Yaku(-1, 'Nagashi Mangan', 5, 5)
renhou = Yaku(36, 'Renhou', None, 5)

# Yaku 1 Hands
pinfu = Yaku(7, 'Pinfu', None, 1)
tanyao = Yaku(8, 'Tanyao', 1, 1)
iipeiko = Yaku(9, 'Iipeiko', None, 1)
haku = Yaku(18, 'Yakuhai (haku)', 1, 1)
hatsu = Yaku(19, 'Yakuhai (hatsu)', 1, 1)
chun = Yaku(20, 'Yakuhai (chun)', 1, 1)
yakuhai_place = Yaku(10, 'Yakuhai (wind of place)', 1, 1)
yakuhai_round = Yaku(11, 'Yakuhai (wind of round)', 1, 1)

# Yaku 2 Hands
sanshoku = Yaku(25, 'Sanshoku Doujun', 1, 2)
ittsu = Yaku(24, 'Ittsu', 1, 2)
chanta = Yaku(23, 'Chanta', 1, 2)
honroto = Yaku(31, 'Honroutou', 2, 2)
toitoi = Yaku(28, 'Toitoi', 2, 2)
sanankou = Yaku(29, 'San Ankou', 2, 2)
sankantsu = Yaku(27, 'San Kantsu', 2, 2)
sanshoku_douko = Yaku(26, 'Sanshoku Doukou', 2, 2)
chiitoitsu = Yaku(22, 'Chiitoitsu', None, 2)
shosangen = Yaku(30, 'Shou Sangen', 2, 2)

# Yaku 3 Hands
honitsu = Yaku(34, 'Honitsu', 2, 3)
junchan = Yaku(33, 'Junchan', 2, 3)
ryanpeiko = Yaku(32, 'Ryanpeikou', None, 3)

# Yaku 6 Hands
chinitsu = Yaku(35, 'Chinitsu', 5, 6)

# Yakuman list
kokushi = Yaku(47, 'Kokushi musou', None, 13, True)
chuuren_poutou = Yaku(45, 'Chuuren Poutou', None, 13, True)
suuankou = Yaku(40, 'Suu ankou', None, 13, True)
daisangen = Yaku(39, 'Daisangen', 13, 13, True)
shosuushi = Yaku(50, 'Shousuushii', 13, 13, True)
ryuisou = Yaku(43, 'Ryuuiisou', 13, 13, True)
suukantsu = Yaku(51, 'Suu kantsu', 13, 13, True)
tsuisou = Yaku(42, 'Tsuu iisou', 13, 13, True)
chinroto = Yaku(44, 'Chinroutou', 13, 13, True)

# Double yakuman
daisuushi = Yaku(49, 'Dai Suushii', 26, 26, True)
daburu_kokushi = Yaku(48, 'Daburu Kokushi musou', None, 26, True)
suuankou_tanki = Yaku(41, 'Suu ankou tanki', None, 26, True)
daburu_chuuren_poutou = Yaku(46, 'Daburu Chuuren Poutou', None, 26, True)

# Yakuman situations
tenhou = Yaku(37, 'Tenhou', None, 13, True)
chiihou = Yaku(38, 'Chiihou', None, 13, True)

# Other
dora = Yaku(52, 'Dora', 1, 1)
aka_dora = Yaku(54, 'Aka Dora', 1, 1)
