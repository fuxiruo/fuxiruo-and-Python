import logging

myui_logger = logging.getLogger('main.{}'.format(__name__))
myui_logger.setLevel(logging.INFO)

class TinyXmlException(Exception):
    pass

class TinyXmlParse:
    """
        <是开始符S，>是终结符号e，/也是终结符f，其他是非终结符号V
        <test/> S->Vef
        <test>  S->Ve
        </test> Sf->Ve
                f->V|e
    """
    def __init__(self) -> None:
        self._now_level = 0
        self._now_index = -1
        self._now_line = ''
        self._token = ''
        self._read_str = ''
        self._data_str = ''
        self._last_ch = None
        self._b_tag_open_start = False
        self._b_tag_close_start = False
        self._b_tag_need_append = False
        self._now_tag = ''
        self._now_attrib_str = ''
        self._b_tag_attrib_start = False
        self._tags = []
        self._continue = ''
        self._start_symbol = ['<']
        self._end_symbol = ['>', '/']

    def feed_line(self, line):
        self._now_line = line
        self._now_index = -1

    def parse(self):
        while self._now_line and self._now_index < len(self._now_line):
            self._token = self._next()
            myui_logger.debug('parse:{}'.format(self._now_line))
            if self._continue == '':
                self._parse_S(self._token)
            elif self._continue == 'data':
                self._parse_data(self._token)
            elif self._continue == 'v':
                self._parse_V(self._token)

        myui_logger.debug('{} end'.format(self._now_line))
        return True

    def check_single_tags(self):
        if len(self._tags) > 0:
            myui_logger.error('tag not close!')
            raise TinyXmlException('tag not close!')

    def _next(self):
        self._now_index = self._now_index + 1
        if self._now_index < len(self._now_line):
            if self._now_index > 0:
                self._last_ch = self._now_line[self._now_index-1]

            self._read_str += self._now_line[self._now_index]
            return self._now_line[self._now_index]
        else:
            return None

    def _parse_S(self, ch):
        self._continue = ''
        if ch is None:
            return
        elif ch.isspace():
            return
        elif ch not in self._start_symbol:
            myui_logger.error('start not found!but:{}'.format(ch))
            raise TinyXmlException('start not found!')

        self._now_tag = ''
        self._now_attrib_str = ''
        myui_logger.debug('start:{}'.format(self._now_level))
        self._token = self._next()
        if self._token == '/': # </test> Sf->Ve
            self._b_tag_close_start = True
            self._now_tag = self._now_tag + self._token
            self._parse_f(self._token)
        else:
            self._b_tag_open_start = True
            self._b_tag_need_append = True
            self._parse_V(self._token)

    def _parse_e(self, ch):
        myui_logger.debug('end:{},{},tag:{}'.format(self._now_level, self._read_str, self._now_tag))
        last_tag = ''
        b_tag_close = False
        if len(self._tags) > 0:
            last_tag = '/' + self._tags[-1]
        if self._read_str.endswith('/>'):
            myui_logger.info('tag self close:{},level:{},_now_attrib_str:{}'.format(self._now_tag, self._now_level, self._now_attrib_str))
            myui_logger.info('-'*50)
        elif last_tag == self._now_tag:
            self._now_level = self._now_level - 1
            myui_logger.info('tag close:{},level:{},data:{}'.format(last_tag, self._now_level, self._data_str))
            myui_logger.info('-'*50)
            self._tags.pop()
            b_tag_close = True
        elif self._b_tag_need_append:
            if self._read_str.strip().startswith('<?'):
                myui_logger.info('tag skip:{}'.format(self._read_str))
                b_tag_close = True
            else:
                myui_logger.info('tag start:{},tag:{},level:{},attrib:{}'.format(self._read_str, self._now_tag,self._now_level,self._now_attrib_str))
                self._tags.append(self._now_tag)
                self._now_level = self._now_level + 1

        self._read_str = ''
        self._token = self._next()
        self._data_str = ''
        self._b_tag_open_start = False
        self._b_tag_close_start = False
        self._b_tag_attrib_start = False
        self._b_tag_need_append = False

        if b_tag_close:
            self._parse_S(self._token)
        else:
            self._parse_data(self._token)

    def _parse_f(self, ch):
        myui_logger.debug('now:{}'.format(self._read_str))
        if self._last_ch == '<': #</test> Sf->Ve
            if self._token != '/':
                raise TinyXmlException('{} expect / but {} found!'.format(self._read_str, self._token))
            else:
                self._token = self._next()
                self._parse_V(self._token)
        else:
            self._token = self._next() #<test/> S->Vef
            if self._token =='>':#V可能含有/
                self._parse_e(self._token)
            else:
                if self._b_tag_attrib_start:
                    self._now_attrib_str = self._now_attrib_str + ch
                self._parse_V(self._token)

    def _parse_data(self, ch):
        # myui_logger.debug('now:{}'.format(self._read_str))
        self._continue = 'data'
        if ch is None:
            myui_logger.warning('{} expect data but end!'.format(self._read_str))
            return
        elif ch in self._start_symbol:
            return self._parse_S(ch)
        elif ch in self._end_symbol and ch == '<': #data可能含有/
            myui_logger.error('{} expect data but {} found!'.format(self._read_str, ch))
            raise TinyXmlException('{} expect data but {} found!'.format(self._read_str, ch))

        self._data_str = self._data_str + ch

    def _parse_V(self, ch):
        self._continue = 'v'
        # myui_logger.debug('now:{}'.format(self._read_str))
        if ch is None:
            myui_logger.warning('{} expect V but end!'.format(self._read_str))
            return
        elif ch in self._start_symbol:
            myui_logger.error('{} expect V|> but {} found!'.format(self._read_str, ch))
            raise TinyXmlException('{} expect V|> but {} found!'.format(self._read_str, ch))
        elif ch in self._end_symbol:
            if ch == '/':
                return self._parse_f(ch)
            else:
                return self._parse_e(ch)

        if self._b_tag_open_start or self._b_tag_close_start:
            if self._b_tag_attrib_start:
                self._now_attrib_str = self._now_attrib_str + ch
            elif ch.isspace():
                self._b_tag_attrib_start = True
            else:
                self._now_tag = self._now_tag + ch
