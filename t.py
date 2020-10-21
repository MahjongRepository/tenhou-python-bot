data = """
1830 Sonoda Ken
1831 Murakami Jun
1832 Suzuki Taro
1833 Maruyama Kanako
1834 Nikaido Aki
1835 Takizawa Kazunori
1836 Katsumata Kenji
1837 Sasaki Hisato
1838 Takamiya Mari
1839 Maehara Yudai
1840 Fujisaki Satoshi
1841 Oi Takaharu
1842 Shiratori Sho
1843 Matsumoto Yoshihiro
1844 Hinata Aiko
1845 Uotani Yumi
1846 Kondo Seiichi
1847 Kayamori Sayaka
1848 Wakutsu Akira
1849 Hagiwara Masato
1850 Setokuma Naoki
1851 Kurosawa Saki
1852 Kobayashi Go
1853 Asakura Koshin
1854 Ishibashi Nobuhiro
1855 Mizuhara Akina
1856 Uchikawa Kotaro
1857 Okada Sayaka
1858 Sawazaki Makoto
1860 Hori Shingo
"""

for x in data.split('\n'):
    if not x:
        continue

    d = x.split(' ')

    player_id = d[0].strip()
    name = d[1].strip() + " " + d[2].strip()

    print(player_id, name)
