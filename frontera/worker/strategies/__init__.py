# -*- coding: utf-8 -*-
from abc import ABCMeta, abstractmethod


class BaseCrawlingStrategy(object):
    """
    Interface definition for a crawling strategy.

    Before calling these methods strategy worker is adding 'state' key to meta field in every
    :class:`Request <frontera.core.models.Request>` with state of the URL. Pleases refer for the states to HBaseBackend
    implementation.

    After exiting from all of these methods states from meta field are passed back and stored in the backend.
    """
    __metaclass__ = ABCMeta

    def __init__(self, mb_stream):
        self._mb_stream = mb_stream

    @classmethod
    def from_worker(cls, manager, mb_scheduler):
        """
        Called on instantiation in strategy worker.

        :param manager: :class: `Backend <frontera.core.manager.FrontierManager>` instance
        :param mb_scheduler: :class: `UpdateScoreStream <frontera.worker.strategy.UpdateScoreStream>` instance
        :return: new instance
        """
        raise cls(mb_scheduler)

    @abstractmethod
    def add_seeds(self, seeds):
        """
        Called when add_seeds event is received from spider log.

        :param list seeds: A list of :class:`Request <frontera.core.models.Request>` objects.
        """
        return {}

    @abstractmethod
    def page_crawled(self, response, links):
        """
        Called every time document was successfully crawled, and receiving page_crawled event from spider log.

        :param object response: The :class:`Response <frontera.core.models.Response>` object for the crawled page.
        :param list links: A list of :class:`Request <frontera.core.models.Request>` objects generated from \
        the links extracted for the crawled page.
        """
        return {}

    @abstractmethod
    def page_error(self, request, error):
        """
        Called every time there was error during page downloading.

        :param object request: The fetched with error :class:`Request <frontera.core.models.Request>` object.
        :param str error: A string identifier for the error.
        """
        return {}

    def finished(self):
        """
        Called by Strategy worker, after finishing processing each cycle of spider log. If this method returns true,
        then Strategy worker reports that crawling goal is achieved, stops and exits.

        :return: bool
        """
        return False

    def close(self):
        """
        Called when strategy worker is about to close crawling strategy.
        """
        pass

    def schedule(self, request, score=1.0, dont_queue=False):
        """
        Schedule document for crawling with specified score.

        :param request: A :class:`Request <frontera.core.models.Request>` object.
        :param score: float from 0.0 to 1.0
        :param dont_queue: bool, True - if no need to schedule, only update the score
        """
        self._mb_stream.send(request.url, request.meta['fingerprint'], score, dont_queue)