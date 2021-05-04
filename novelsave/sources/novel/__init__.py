from .betwixtedbutterfly import BetwixtedButterfly
from .boxnovel import BoxNovel
from .chickengage import ChickEngage
from .chrysagarden import Chrysanthemumgarden
from .dragontea import DragonTea
from .dummynovels import DummyNovels
from .fanfiction import Fanfiction
from .foxaholic import Foxaholic
from .insanitycave import InsanityCave
from .kieshitl import KieshiTl
from .ktlchamber import Ktlchamber
from .lightnovelworld import LightNovelWorld
from .mtlnovel import MtlNovel
from .novelfull import NovelFull
from .novelonlinefull import NovelOnlineFull
from .novelsite import NovelSite
from .peachpitting import PeachPitting
from .readlightnovel import ReadLightNovel
from .royalroad import RoyalRoad
from .scribblehub import ScribbleHub
from .spacebattles import Spacebattles
from .sufficientvelocity import SufficientVelocity
from .wattpad import WattPad
from .webnovel import Webnovel
from .wuxiaco import WuxiaCo
from .wuxiacom import WuxiaCom
from .wuxiaonline import WuxiaOnline
from .novelpassion import NovelPassion
from ...exceptions import MissingSource

sources = [
    Webnovel,
    WuxiaCo,
    BoxNovel,
    ReadLightNovel,
    InsanityCave,
    Ktlchamber,
    LightNovelWorld,
    KieshiTl,
    ScribbleHub,
    MtlNovel,
    Fanfiction,
    NovelFull,
    WuxiaCom,
    RoyalRoad,
    Spacebattles,
    WattPad,
    SufficientVelocity,
    DragonTea,
    NovelSite,
    Foxaholic,
    Chrysanthemumgarden,
    PeachPitting,
    BetwixtedButterfly,
    DummyNovels,
    ChickEngage,
    WuxiaOnline,
    NovelOnlineFull,
    NovelPassion,
]


def parse_source(url):
    """
    create source object to which the :param url: belongs to

    :return: source object
    """
    for source in sources:
        if source.of(url):
            return source()

    raise MissingSource(url)
