import mailbox
import email
import email.utils
import email.header
import logging
import calendar
import locale

import src.message
import src.uploader
from bs4 import BeautifulSoup


class Parser:
    _mbox_path: str = None
    _uploader: src.Uploader = None
    _parse_body: bool = False

    def __init__(self, mbox_path: str, uploader: src.Uploader):
        logging.info("Init parser for file: %s" % mbox_path)
        self._mbox_path = mbox_path
        self._uploader = uploader

    def parse(self, body: bool = False, skip: int = 0, batch_size: int = 500):
        batch = list()
        count = 0
        skipped = 0
        inserted = 0
        self._parse_body = body

        logging.info("Start parsing...")

        for msg in mailbox.mbox(self._mbox_path, mailbox.mboxMessage, False):
            count += 1

            if count < skip:
                continue

            item = self._parse_message(msg)

            if item:
                batch.append(item.get())
                inserted += 1
                # pprint(item.get())
                # self._uploader.insert(item.get())
                if len(batch) == batch_size:
                    self._uploader.insert_batch(batch)
                    logging.info("Upload: %s - upload total messages processed: %6d" % ("OK", count))
                    batch = list()
            else:
                skipped += 1

        if len(batch) > 0:
            self._uploader.insert_batch(batch)
            logging.info("Upload: %s. Total messages processed: %6d" % ("OK", count))

        logging.info("Parsing complete. %d messages inserted, %d items skipped" % (inserted, skipped))

    def _validate_message(self, message):
        if 'message-id' not in message:
            logging.debug("Message don't have 'message-id'")
            return False

        result = {}

        for (k, v) in message.items():
            result[k.lower()] = v

        if "from" not in result:
            logging.debug("Message don't have 'from' :: %s" % result)
            return False

        if "to" not in result:
            logging.debug("Message don't have 'to' :: %s" % result)
            return False

        if "date" not in result:
            logging.debug("Message don't have 'date' :: %s" % result)
            return False

        if "subject" not in result:
            logging.debug("Message don't have 'subject' :: %s" % result)
            return False

        return result

    def _parse_message(self, msg):
        result = self._validate_message(msg)

        if not result:
            return None

        for k in ['to', 'cc', 'bcc']:
            if not result.get(k):
                continue

            emails = self._decode_header(result[k]) \
                .replace('\n', '') \
                .replace('\t', '') \
                .replace('\r', '') \
                .replace(' ', '') \
                .encode('utf8') \
                .decode('utf-8', 'ignore') \
                .split(',')

            result[k] = [self._normalize_email(e) for e in emails]
            del emails

        result['from'] = self._normalize_email(self._decode_header(result['from']))

        try:
            tt = email.utils.parsedate_tz(result['date'])
            tz = tt[9] if len(tt) == 10 and tt[9] else 0
            result['date_ts'] = int(calendar.timegm(tt) - tz) * 1000
        except:
            logging.debug("Can't parse timestamp of 'date' :: %s" % result)
            return None

        result['subject'] = self._decode_header(result["subject"])

        if "x-gmail-labels" in result:
            labels = []
            result["x-gmail-labels"] = self._decode_header(result["x-gmail-labels"])

            for l in result["x-gmail-labels"].split(','):
                labels.append(l.strip().lower())

            del result["x-gmail-labels"]
            result['labels'] = labels

        # todo: repair parse bodies
        # Have fatal error with big messages. They can't insert in mongo, beacuse bson have limit
        #
        # Bodies...
        # if self._parse_body:
        #     result['body'] = ''
        #
        #     if msg.is_multipart():
        #         for mpart in msg.get_payload():
        #             if mpart is not None:
        #                 mpart_payload = mpart.get_payload(decode=True)
        #                 if mpart_payload is not None:
        #                     result['body'] += self._strip_html_css_js(mpart_payload)
        #     else:
        #         result['body'] = self._strip_html_css_js(msg.get_payload(decode=True))

        # parts = result.get("parts", [])
        # result['content_size_total'] = 0
        # for part in parts:
        #     result['content_size_total'] += len(part.get('content', ""))

        return src.Message(
            result.get('message-id'),
            result.get('from'),
            result.get('to'),
            result.get('date'),
            result.get('date_ts'),
            result.get('subject'),
            result.get('labels'),
            result.get('body')
        )

    def _normalize_email(self, email_in):
        parsed = email.utils.parseaddr(email_in)
        return parsed[1]

    def _strip_html_css_js(self, msg):
        soup = BeautifulSoup(msg, "html.parser")  # create a new bs4 object from the html data loaded
        for script in soup(["script", "style"]):  # remove all javascript and stylesheet code
            script.extract()
        # get text
        text = soup.get_text()
        # break into lines and remove leading and trailing space on each
        lines = (line.strip() for line in text.splitlines())
        # break multi-headlines into a line each
        chunks = (phrase.strip() for line in lines for phrase in line.split("  "))
        # drop blank lines
        text = '\n'.join(chunk for chunk in chunks if chunk)
        return text

    def _decode_header(self, header, content_charset=None):
        if header is None: return ""
        parts = []
        if content_charset is None:
            content_charset = 'utf-8'

        # decode from base64
        for part in email.header.decode_header(header):
            header_string, charset = part

            if charset in ['unknown-8bit', None]:
                charset = content_charset

            decoded_part = self._try_decode(header_string, charset)
            parts.append(decoded_part)

        return "".join(parts)

    def _try_decode(self, decoded_part, charset):
        # bytes to string
        try:
            decoded_part = decoded_part.decode(charset)
        except:
            try:
                # bytes to string with local system charset
                decoded_part = decoded_part.decode(locale.getpreferredencoding())
            except:
                # bytes to string without decodind
                decoded_part = str(decoded_part)
        return decoded_part
