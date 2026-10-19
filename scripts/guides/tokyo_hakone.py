"""Editorial layer for the Tokyo + Hakone guide.

The itinerary itself (entries, times, costs, pins) comes from the Roamly trip in
tokyo-hakone.trip.json. This file only holds what a guide adds on top: the
headline, prose per day, photos, tips and suggested companion edits.
"""
SLUG = "tokyo-hakone-7-day-itinerary"
TRIP = "tokyo-hakone.trip.json"
CT = "blog-tokyo-hakone-7d"
TITLE = "7 Days in Tokyo and Hakone: Neon Nights, Hot Springs and Mount Fuji"
SEO_TITLE = "7-Day Tokyo and Hakone Itinerary for Couples (with Costs) | Roamly"
DESCRIPTION = ("A 7-day Tokyo and Hakone itinerary for two: Shinjuku nights, Asakusa mornings, a bullet train to the "
               "hot springs and a lake cruise toward Mount Fuji. Day-by-day times, costs and a map.")
CRUMBS = ["Guides", "Japan", "7-day itineraries"]
DEK = ("Four unhurried days in Tokyo, split by neighborhood, then two nights in Hakone where the trains slow down, "
       "the baths get hotter and Mount Fuji fills the far end of Lake Ashi on a clear morning.")
HERO = ("tk-hero", "Kabukichō in Shinjuku, a ten-minute walk from day one's hotel", (1.6, 0.18))
UPDATED = "October 19, 2026"
READ_MIN = 12
GLANCE = [("Length", "7 days, 6 nights"), ("Route", "Tokyo → Hakone → Tokyo"),
          ("Best for", "Couples who like late nights"), ("On the ground", "{total} for two"),
          ("Best months", "Mar–May, Oct–Nov")]
INTRO = [
    "Most first-time Tokyo plans cram a day trip into every gap. This one does the opposite. Each Tokyo day stays in one part of the city, so you spend your time in neighborhoods instead of on the subway, and Hakone gets two nights rather than a rushed day trip. You get the mountain railway, the volcanic valley, an onsen and a cruise on Lake Ashi without watching the clock for the last train back.",
    "I built this trip in Roamly's AI trip planner for a couple traveling in mid-October, then checked every stop and rewrote the parts I'd do differently. The plan below is the trip exactly as it appears in Roamly, costs included, and it's one tap away if you want to make it yours.",
]
TRIP_LABEL = "Tokyo & Hakone"
FLIGHTS_NOTE = "Flights are separate: round trips from Washington, DC came to about $2,400 per person."

DAYS = [
 dict(area="Shinjuku", title="Shinjuku after dark",
  before=[("tk-tmg", "Tokyo Metropolitan Government Building"), ("tk-omoide", "A yakitori counter in Omoide Yokocho")],
  prose=["Keep the first day light. Drop your bags at Hotel Gracery Shinjuku, the one with a life-size Godzilla head on its terrace, and wait for dark. The city is at its most dramatic from above at night, and the best free view is a ten-minute walk west.",
         "The Tokyo Metropolitan Government Building has observation decks on the 45th floor that cost nothing to visit. Tokyo runs to the horizon in every direction. Afterwards, walk back toward the station to Omoide Yokocho, a tangle of narrow alleys where yakitori counters seat half a dozen people under a haze of charcoal smoke."],
  tip="<b>Carry cash.</b> Many of the smallest counters in Omoide Yokocho don't take cards, and some add a small seating charge."),
 dict(area="Asakusa · Akihabara", title="Old Tokyo in the morning, electric Tokyo by afternoon",
  before=[("tk-sensoji", "Sensō-ji's main hall, past the Kaminarimon gate and Nakamise street")],
  prose=["Sensō-ji is Tokyo's oldest temple, and it is busiest from late morning, so aim to walk under the giant red lantern of the Kaminarimon gate by 9:30. The approach, Nakamise-dori, is a few hundred meters of snack and souvenir stalls. Try ningyo-yaki, small sponge cakes filled with red bean paste, while they're still warm.",
         "Lunch is gyukatsu, a beef cutlet fried quickly so the inside stays rare, which you finish on a hot stone at the table. Then hop over to Akihabara for multi-story electronics stores, retro game shops and arcades stacked six floors high. Dinner is soba at Kanda Matsuya, served from the same pre-war wooden building for generations."],
  after=[("tk-akiba", "Akihabara after dark")],
  tip="<b>Go on a Sunday if you can.</b> Akihabara's main street, Chuo-dori, closes to cars on Sunday afternoons."),
 dict(area="Harajuku · Shibuya", title="Forest shrine, street fashion and the famous crossing",
  before=[("tk-meiji", "Meiji Jingu's main shrine"), ("tk-take2", "Shops on Takeshita Street")],
  prose=["Start somewhere quiet. Meiji Jingu sits in a forest of around 100,000 trees donated from across Japan when the shrine was built, and it takes ten minutes of gravel paths under huge wooden torii to reach the main hall. Leave through the south gate and you are a block from Takeshita Street, Harajuku's narrow lane of fashion shops and giant crepes.",
         "Harajuku Gyozaro keeps its menu short: pan-fried or steamed gyoza, a few sides, and a line that moves quickly. Walk down to Shibuya Crossing after lunch. Crossing it is the experience, but the view from above explains it, so book a sunset slot at Shibuya Sky on top of Shibuya Scramble Square. End with live music in Shibuya's small clubs."],
  after=[("tk-shibuya", "Shibuya Crossing from above")],
  edit="Add Shibuya Sky at 4:30 pm on day 3"),
 dict(area="Hakone", title="Bullet train, mountain railway and a volcanic valley",
  before=[("tk-tozan3", "Hakone Tozan car No. 103 at Gōra"), ("tk-owakudani", "Steam vents at Ōwakudani under the ropeway")],
  prose=["Take the Shinkansen from Tokyo Station to Odawara, about 35 minutes on the faster trains, and buy a Hakone Freepass when you arrive. It covers the mountain railway, cable car, ropeway, Lake Ashi boats and most local buses, which turns Hakone into one loop instead of a stack of tickets.",
         "The Hakone Tozan Railway climbs slowly through forested switchbacks to Gōra. Stop for lunch at Gyoza Center, then ride the ropeway over Ōwakudani, an active volcanic valley where steam pours out of yellow rock. The black eggs sold at the top are boiled in the hot springs, and local legend says each one adds seven years to your life. End the day in a hot spring. If your hotel in Gōra has its own baths, use those and skip the ride back down to Yumoto."],
  tip="<b>Check the ropeway status that morning.</b> It sometimes pauses when volcanic gas levels rise. The Freepass still covers the buses around the closed section."),
 dict(area="Lake Ashi", title="A torii in the water and the old Tōkaidō road",
  before=[("tk-ashi", "Mount Fuji over Lake Ashi, with Hakone Shrine's torii at the water's edge")],
  prose=["Mornings are when Fuji is most likely to show itself, so be at Hakone Shrine early. Its red torii stands in the shallows of Lake Ashi, and a forest path of cedars leads up to the main shrine. Then board the sightseeing cruise across the lake and watch for the mountain at the far end.",
         "Lunch is at Bakery & Table near Moto-Hakone, where the terrace has a footbath you can soak in while you eat. In the afternoon, walk a section of the old Tōkaidō, the Edo-period highway between Tokyo and Kyoto. The stones are still there under giant cedars, and the path leads to Amazake-chaya, a thatched teahouse that has served travelers for around 400 years."],
  after=[("tk-tokaido", "Cedars along the old Tōkaidō"), ("tk-amazake", "Amazake-chaya teahouse")],
  tip="<b>We moved the teahouse earlier.</b> Roamly's first draft had it at 5:30 pm, but it closes in the late afternoon. Start the walk by 2."),
 dict(area="Shimokitazawa · Roppongi", title="Back to Tokyo for vintage shops and a rock bar",
  before=[("tk-shimokita", "An afternoon in Shimokitazawa")],
  prose=["Take the Odakyu Romancecar from Hakone-Yumoto straight to Shinjuku, about 85 minutes. Shimokitazawa is a few minutes away on the same line: Tokyo's best neighborhood for vintage clothes, record shops and small cafés in narrow lanes.",
         "Eat early at Shirube, a loud and cheerful izakaya known for its blowtorched mackerel. Then cross town to Roppongi for craft beer at BrewDog and a late set at Bauhaus, a tiny rock bar where the staff are the house band."],
  edit="Swap the Roppongi bars for Golden Gai"),
 dict(area="Tsukiji · Ginza", title="Market breakfast and one last bowl of ramen",
  before=[("tk-tsukiji", "A stall in the Tsukiji outer market"), ("tk-ginzasix", "Ginza Six")],
  prose=["The famous tuna auction moved to Toyosu in 2018, but the Tsukiji outer market is still the best breakfast in Tokyo. Graze from stall to stall: sea urchin, wagyu skewers, thick slices of tamagoyaki and sushi at a counter. Most stalls wind down by early afternoon.",
         "Walk to Ginza Six for its free rooftop garden, then join the line at Ginza Kagari for creamy chicken paitan ramen before the airport. Haneda is about 30 minutes from Ginza by train."]),
]

PRACTICAL = """
<h2>Getting around</h2>
<p><b>Add a Suica or PASMO card to Apple Wallet</b> before you land. It works on almost every train, subway and bus in Tokyo and Hakone. <b>Skip the Japan Rail Pass</b> for this route and buy the <b>Hakone Freepass</b> instead. <b>Send your luggage ahead</b> with takkyubin, the next-day delivery service hotels and convenience stores offer, and travel to Hakone with a day bag.</p>
<h2>When to go</h2>
<p>October and November bring mild weather, autumn color in Hakone and some of the year's clearest skies for Fuji. Late March to early April brings cherry blossoms and crowds. Summer is hot and hazy, and Fuji often hides.</p>
"""
FAQ = [
 ("Is 7 days enough for Tokyo and Hakone?", "Yes. Four days covers Tokyo's main neighborhoods at a comfortable pace, and two nights in Hakone lets you do the full loop of railway, ropeway, lake and onsen without rushing back for the last train."),
 ("Do I need a Japan Rail Pass for Tokyo and Hakone?", "No. This route only uses one long train ride each way, which costs much less than a 7-day pass. Use a Suica or PASMO card for local trains and buy a Hakone Freepass."),
 ("How much does a week in Tokyo and Hakone cost?", "Roamly estimates about {total} for two people on the ground, covering mid-range hotels, food, local transport and paid sights. That's roughly {each} each, before international flights."),
 ("Can you see Mount Fuji from Hakone?", "Often, but not always. Your best chances are early mornings from October to February, from the Lake Ashi cruise and around Hakone Shrine."),
]
