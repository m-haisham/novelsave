from .source import Source
from .webnovel import Webnovel
from .boxnovel import BoxNovel
from .scribblehub import ScribbleHub
from .insanitycave import InsanityCave
from .kieshitl import KieshiTl
from .ktlchamber import Ktlchamber
from .lightnovelworld import LightNovelWorld
from .readlightnovel import ReadLightNovel
from .webnovel import Webnovel
from .wuxiaco import WuxiaCo
from .mtlnovel import MtlNovel
from .fanfiction import Fanfiction
from .novelfull import NovelFull
from .wuxiacom import WuxiaCom
from .royalroad import RoyalRoad
from .spacebattles import Spacebattles
from .wattpad import WattPad
from .sufficientvelocity import SufficientVelocity
from .dragontea import DragonTea
from .novelsite import NovelSite
from ..exceptions import MissingSource

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
]


def parse_source(url):
    """
    create source object to which the :param url: belongs to

    :return: source object
    """
    for source in sources:
        if source.of(url):
            return source()

    raise MissingSource(url, f'"{url}" does not belong to any available source')
