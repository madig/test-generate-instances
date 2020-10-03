import ufoLib2

for p in [
    "NotoSans-Bold.ufo",
    "NotoSans-Condensed.ufo",
    "NotoSans-CondensedBold.ufo",
    "NotoSans-CondensedLight.ufo",
    "NotoSans-CondensedSemiBold.ufo",
    "NotoSans-Light.ufo",
    "NotoSans-Regular.ufo",
    "NotoSans-SemiBold.ufo",
]:
    ufoLib2.Font.open(p, lazy=False)
