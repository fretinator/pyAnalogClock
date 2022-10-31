#! /usr/bin/python
import feedparser
import webbrowser
import tempfile


class MyFeedParser:
    feeds = {
        'http://rss.cnn.com/rss/cnn_topstories.rss'
    }

    def __init(self):
        self.output = ""

    def getLatestFeedItems(self):
        myItems = []

        for feed in MyFeedParser.feeds:
            d = feedparser.parse(feed);

            # Try to get date the current feed was built

            # print("--------------------------------")
            # print("Reading " + d.feed.title + "...")
            # print d.feed.subtitle
            # print("--------------------------------")

            for post in d.entries:
                if not (hasattr(post, 'updated')) and hasattr(post, 'pubDate'):
                    post['updated'] = post['pubDate']

                myItems.append(post)

        myItems.sort(reverse=True, key=lambda item: item.updated if hasattr(item, 'updated') else "zzzzzzzz")

        return myItems

    def printLatestFeeds(self, detailed=False):
        print("Starting")

        myItems = self.getLatestFeedItems()

        for item in myItems:
            print(item.title)
            print(item.link)
            if hasattr(item, 'updated'):
                print(item.updated + "\n")
            else:
                print("Unknown update time\n")

            if detailed:
                print(item.summary)

        print("Ending")

    def getLatestFeedsAsHtml(self, detailed=False):
        retval = "<HTML><HEAD><title>My Feed Parser</title></HEAD>\n"

        myItems = self.getLatestFeedItems()

        retval += "\t<BODY>\n\n"

        # start of list of feed data
        retval += "<ul>"
        for item in myItems:
            retval += "<ht>\n"
            retval += "<p>\n"
            retval += "<li>" + item.title + "</li>\n"
            retval += "<li><a href=\"" + item.link + "\">LINK</a></li>\n"

            if hasattr(item, 'updated'):
                retval += "<li>" + item.updated + "<li>\n"
            else:
                retval += "<li>" + "Unknown update time</li>\n"

            if detailed:
                retval += "<li>" + item.summary + "</li>\n"

            retval += "</p>\n"

        retval += "</ul>\n"

        retval += "</BODY></HTML>\n"
        return retval


if __name__ == "__main__":
    # print("Start feed parser app")

    f = MyFeedParser()

    s = f.getLatestFeedsAsHtml(True)
    # print(s)

    fh, path = tempfile.mkstemp(suffix='.html')
    url = 'file://' + path

    with open(path, 'w') as fp:
        fp.write(s)

    webbrowser.open(url)
