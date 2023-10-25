import sqlite3

# Add any new content to the list, in the right section
dictionary = {"cars": ['EXCALIBUR', 'MCLAREN P1', 'CATALYST', 'LAND ROVER DEFENDER', 'ETHER', 'DISRUPTOR', 'TITAN', 'ROCKETFOX', 'MANTA', 'NISSAN GT-R NISMO', 'BUGATTI LVN', 'PORSCHE 911 GT2 RS', 'ASTON MARTIN VANQUISH', 'BLADE', 'ZEPHYRUS', 'HELIOS', 'FARADAY', 'FORD MUSTANG', 'CHEVROLET CAMARO ZL1', 'LOTUS GT430', 'FORD GT', 'BMW M8 GTE', 'FORD F-150', 'ASTON MARTIN DB11', 'JUGGLER', 'BMW I8', 'ARES', 'BMW M4 RACING', 'VOLKSWAGEN I.D. R', 'LYNK & CO 03', 'MINI JCW', 'BMW X5', 'SINGULARITY', 'VOLKSWAGEN BEETLE', 'FORD FOCUS RS', 'SHINING', 'INFINITY PROTOTYPE', 'PAGANI HUAYRA', 'ZEN', 'KSANA', 'PALADIN', 'BEACH WAYFARER'],
"maps": ['SU CAUSEWAY', 'JIANGNAN', 'MOUNTAIN CITY', 'LONGJING TEA GARDEN', 'ECLIPSE', 'NIGHT JUNCTION', "HERO'S ROAD", 'REAPPEARING ISLAND', 'SUNSET BOULEVARD', 'LOFOTEN ISLANDS', 'CANYON CROSSING', 'HIGHWAY INTERCHANGE', 'GOLDEN HAND TRACK', 'ARCTIC RALLY', 'SKY BRIDGE', 'COASTAL STORM', 'MT. HARUNA', 'DAM SPEEDWAY', 'SPEED CIRCUIT', "HEAVEN'S PATH", 'YARDANG RALLY', 'AIRPORT RUNWAY', 'ROUTE 65', 'VILLAGE', 'CLIFF EDGE', 'TORII GATE', 'MIDNIGHT NEON', 'ACE ACADMEY', 'SAKURA RIDGE'],
"ecus": ['ROUND', 'DIAMOND', 'HEXAGON', 'TRIANGLE', 'V-SHAPED', 'CORE']}

with sqlite3.connect("project.db") as con:
    cur = con.cursor()
    for section, items in dictionary.items():
        for item in items:

            # Check if an item is already in database
            res = cur.execute("SELECT * FROM options WHERE section = ? AND item = ?", (section, item))
            if res.fetchone() == None:

                # Add the item if not already in database
                cur.execute("INSERT INTO options (section, item) VALUES (?, ?)", (section,item))
                print("success:",item)
            else:
                
                # Skip item if it already exists
                continue