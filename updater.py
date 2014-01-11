#!/usr/bin/env python
# Provides a class to use in a self updating script for RSS feeds.
# Modified from DanielGibbsNZ's updater.py.

import thundermaps
import rss
import time
from datetime import datetime
from time import strptime

class Updater:

    def __init__(self, key, account_id, url, categories):
        self.tm_obj = thundermaps.ThunderMaps(key)
        self.feed_obj = rss.Feed(url)
        self.account_id = account_id
        self.categories = categories

    def start (self):
        # Try to load the source_ids already posted.
        source_ids = []
        try:
            source_ids_file = open(".source_ids_sample", "r")
            source_ids = [i.strip() for i in source_ids_file.readlines()]
            source_ids_file.close()
        except Exception as e:
            print "! WARNING: No valid cache file was found. This may cause duplicate reports."

        # Run until interrupt received.
        print "* Updating..."
        while True:
            # Load the data 
            items = self.feed_obj.getFeed()

            # Create reports for the listings.
            reports = []
            for item in items:
                # Create the report, filling in the fields using fields from the RSS obj
                report = {
                    "latitude": -41.2889,
                    "longitude": 174.7772,
                    "category_id": self.categories[item.getCategory()],
                    "occurred_on": item.getDateTime().strftime('%H:%M%p %d/%m/%Y'),
                    "description": item.getDescription(),
                    }
		# Add the report to the list of reports if it hasn't already been posted.
		if report["occurred_on"] not in source_ids:
			reports.append(report)
		source_ids.append(report["occurred_on"])

            # If there is at least one report, send the reports to Thundermaps.
            if len(reports) > 0:
		print "[%s] Sending %d reports to Thundermaps..." % (time.strftime("%c"), len(reports))
		# Upload 10 at a time.
		for some_reports in [reports[i:i+10] for i in range(0, len(reports), 10)]:
			self.tm_obj.sendReports(self.account_id, some_reports)
		print "* Done."
				  
            try:
		source_ids_file = open(".source_ids_sample", "w")
		for i in source_ids:
			source_ids_file.write("%s\n" % i)
		source_ids_file.close()
            except Exception as e:
		print "! WARNING: Unable to write cache file."
		print "! If there is an old cache file when this script is next run, it may result in duplicate reports."

            print "* Update completed."

            # Wait half an hour before trying again.
            if reports == []:
		print "* No new entries added."
            time.sleep(30 * 60)