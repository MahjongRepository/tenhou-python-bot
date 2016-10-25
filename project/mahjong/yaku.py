class Yaku(object):
    name = ''
    han = {'open': None, 'closed': None}
    is_yakuman = False

    def __init__(self, name, open_value, closed_value, is_yakuman=False):
        self.name = name
        self.han = {'open': open_value, 'closed': closed_value}
        self.is_yakuman = is_yakuman

    def __str__(self):
        if self.name == 'Dora':
            return 'Dora {}'.format(self.han['open'])
        else:
            return self.name

    # for calls in array
    def __repr__(self):
        return self.__str__()

# Yaku situations
tsumo = Yaku('Menzen Tsumo', None, 1)
riichi = Yaku('Riichi', None, 1)
ippatsu = Yaku('Ippatsu', None, 1)
daburu_riichi = Yaku('Double Riichi', None, 2)
haitei = Yaku('Haitei Raoyue', 1, 1)
houtei = Yaku('Houtei Raoyui', 1, 1)
rinshan = Yaku('Rinshan Kaihou', 1, 1)
chankan = Yaku('Chankan', 1, 1)
nagashi_mangan = Yaku('Nagashi Mangan', 5, 5)
renhou = Yaku('Renhou', None, 5)

# Yaku 1 Hands
pinfu = Yaku('Pinfu', None, 1)
tanyao = Yaku('Tanyao', 1, 1)
iipeiko = Yaku('Iipeiko', None, 1)
haku = Yaku('Yakuhai (haku)', 1, 1)
hatsu = Yaku('Yakuhai (hatsu)', 1, 1)
chun = Yaku('Yakuhai (chun)', 1, 1)
yakuhai_place = Yaku('Yakuhai (wind of place)', 1, 1)
yakuhai_round = Yaku('Yakuhai (wind of round)', 1, 1)

# Yaku 2 Hands
sanshoku = Yaku('Sanshoku Doujun', 1, 2)
ittsu = Yaku('Ittsu', 1, 2)
chanta = Yaku('Chanta', 1, 2)
honroto = Yaku('Honroutou', 2, 2)
toitoi = Yaku('Toitoi', 2, 2)
sanankou = Yaku('San Ankou', 2, 2)
sankantsu = Yaku('San Kantsu', 2, 2)
sanshoku_douko = Yaku('Sanshoku Doukou', 2, 2)
chiitoitsu = Yaku('Chiitoitsu', None, 2)
shosangen = Yaku('Shou Sangen', 2, 2)

# Yaku 3 Hands
honitsu = Yaku('Honitsu', 2, 3)
junchan = Yaku('Junchan', 2, 3)
ryanpeiko = Yaku('Ryanpeikou', None, 3)

# Yaku 6 Hands
chinitsu = Yaku('Chinitsu', 5, 6)

# Yakuman list
kokushi = Yaku('Kokushi musou', None, 13, True)
chuuren_poutou = Yaku('Chuuren Poutou', None, 13, True)
suuankou = Yaku('Suu ankou', None, 13, True)
daisangen = Yaku('Daisangen', 13, 13, True)
shosuushi = Yaku('Shousuushii', 13, 13, True)
ryuisou = Yaku('Ryuuiisou', 13, 13, True)
suukantsu = Yaku('Suu kantsu', 13, 13, True)
tsuisou = Yaku('Tsuu iisou', 13, 13, True)
chinroto = Yaku('Chinroutou', 13, 13, True)

# Double yakuman
daisuushi = Yaku('Dai Suushii', 26, 26, True)
daburu_kokushi = Yaku('Daburu Kokushi musou', None, 26, True)
suuankou_tanki = Yaku('Suu ankou tanki', None, 26, True)
daburu_chuuren_poutou = Yaku('Daburu Chuuren Poutou', None, 26, True)

# Yakuman situations
tenhou = Yaku('Tenhou', None, 13, True)
chiihou = Yaku('Chiihou', None, 13, True)

# Other
dora = Yaku('Dora', 1, 1)
aka_dora = Yaku('Aka Dora', 1, 1)
