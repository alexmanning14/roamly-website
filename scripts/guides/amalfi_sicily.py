"""Editorial layer for the Amalfi Coast + Sicily guide (trip 3FB6FB54, published 58053BFD)."""
SLUG = "amalfi-coast-sicily-7-day-itinerary"
TRIP = "amalfi-sicily.trip.json"
CT = "blog-amalfi-sicily-7d"
TITLE = "7 Days on the Amalfi Coast and in Sicily: Positano, Capri, Ravello and Taormina"
SEO_TITLE = "7-Day Amalfi Coast and Sicily Itinerary for Couples (with Costs) | Roamly"
DESCRIPTION = ("A mid-range 7-day itinerary for two: Positano, a boat day around Capri, Ravello and Amalfi, then a short flight "
               "to Taormina for Etna wine, the Alcantara gorge and Isola Bella. Day-by-day times, costs and a map.")
CRUMBS = ["Guides", "Italy", "7-day itineraries"]
DEK = ("Three nights in Positano with a boat day on Capri and a walk from Ravello down to Amalfi, then a short flight to "
       "Sicily for three nights in Taormina, Etna's vineyards and the beach at Isola Bella.")
HERO = ("am-pos3", "Positano at dusk, home for the first three nights", (2.1, 0.55))
UPDATED = "October 19, 2026"
READ_MIN = 12
TRIP_LABEL = "Amalfi Coast & Sicily"
LAST_DAY_CHIP = "Fly home from Catania"
FLIGHTS_NOTE = "Flights are separate: Roamly priced them at about $1,890 per person, including the hop from Naples to Catania."
GLANCE = [("Length", "7 days, 6 nights"), ("Route", "Positano → Taormina"),
          ("Best for", "Couples on a mid-range budget"), ("On the ground", "{total} for two"),
          ("Best months", "May–Jun, Sep–Oct")]
INTRO = [
    "Southern Italy's two most famous coasts are only an hour's flight apart, and this week puts them together: three nights in Positano, then three in Taormina. You see Capri from the water, Ravello's gardens, an afternoon of wine on Etna and the Greek theatre in Taormina, without packing and unpacking every other day.",
    "I made this trip in Roamly for a couple traveling in May on a mid-range budget. Costs are Roamly's estimates for two people, about $3,800 on the ground for the whole week, and the plan below is the trip exactly as it appears in Roamly.",
]
VIDEO = ("video/sicily-generation.mp4", "video/sicily-generation-poster.jpg")
MAKE_TITLE = "Made in about 90 seconds. Yours in one tap."
MAKE_BODY = ("This is what making a trip in Roamly looks like: pick a place, tap through dates, budget and vibe, and the planner "
             "builds the week. The recording shows a Sicily trip; this one was made the same way. Open it and it's yours to change. "
             "Tell the trip companion something like “add the ferry back from Capri” or “we land at 6 am on day 1”, and it "
             "rewrites those days and keeps the rest.")

DAYS = [
 dict(area="Positano", title="Arrive in Positano",
  before=[("am-pos4", "Positano's houses stacked down the cliff")],
  prose=["Land in Naples and take a private transfer down the coast, about 90 minutes. Positano tumbles down its cliff to the beach in pastel stacks, and your hotel on Viale Pasitea, the road that zigzags through town, sits halfway between the top and the sea.",
         "Late lunch is at Da Vincenzo, a family-run trattoria on the same road, known for traditional Campanian cooking. Spend the afternoon wandering down the lanes to Spiaggia Grande, and at sunset have a limoncello on a balcony as the town lights come on."],
  tip="<b>Positano is mostly stairs.</b> Pack light and wear shoes with grip. A small local bus runs up and down Viale Pasitea when your legs give out."),
 dict(area="Capri", title="A boat day around Capri",
  before=[("am-far2", "The Faraglioni off Capri's south coast"), ("am-piaz1", "The Piazzetta, Capri's tiny main square")],
  prose=["Take an early ferry from Positano to Capri, about 40 minutes in season. Have a cappuccino near the harbor, then meet your captain at Marina Grande for a gozzo, a traditional wooden boat. The trip circles the island to the Faraglioni, the three rock stacks off the south coast, with stops to swim in coves you can't reach on foot.",
         "Lunch is at La Fontelina, the beach club and restaurant on the rocks right below the Faraglioni. Afterwards, ride up to the Piazzetta for a gelato and some people watching, then take an evening ferry back to Positano."],
  after=[("am-marina3", "Boats in the harbor at Marina Grande")],
  tip="<b>Book the ferry back.</b> Positano–Capri boats run in season only, and the last departure can be early in the evening. Roamly's plan doesn't include the ferries yet, so add them.",
  edit="Add the ferry back from Capri at 6:30 pm"),
 dict(area="Ravello · Amalfi", title="Ravello's gardens and the steps down to Amalfi",
  before=[("am-cimbrone", "The Terrace of Infinity at Villa Cimbrone"), ("am-duomo", "Amalfi Cathedral's bell tower")],
  prose=["Ravello sits on a ridge above Amalfi, quieter and greener than the towns at sea level, about 45 minutes from Positano. After breakfast with a view, walk to Villa Cimbrone, whose gardens end at the Terrace of Infinity: a balcony of marble busts with nothing beyond it but sky and sea.",
         "Then walk down to Amalfi on the old stone paths through lemon terraces, roughly an hour and mostly downhill. Lunch is on the waterfront at Lido Azzurro, and the afternoon is for Amalfi Cathedral, its tiled bell tower and its Cloister of Paradise. A ferry or bus takes you back to Positano."],
  after=[("am-coast", "Looking down the Amalfi Coast toward Salerno")],
  tip="<b>The walk down from Ravello is all steps.</b> It's easy on the lungs and hard on the knees, so take it slowly."),
 dict(area="Taormina", title="Fly to Sicily and settle into Taormina",
  before=[("si-corso", "Corso Umberto, Taormina's main street")],
  prose=["Leave Positano early for Naples airport, about 90 minutes, for the short flight to Catania. It's under an hour in the air, then about an hour by car up to Taormina. Hotel Villa Belvedere, with its garden and pool looking out to sea, is a short walk from the center.",
         "In the evening, stroll Corso Umberto, the pedestrian main street, and have dinner at Trattoria da Nino. Order the pasta alla Norma, Sicily's dish of tomato, fried eggplant and salted ricotta."],
  tip="<b>One thing to add:</b> Roamly's plan starts the day at the airport, so give yourself the drive from Positano. A 7:30 am pickup is comfortable for a late-morning flight.",
  edit="Add a 7:30 am transfer to Naples airport"),
 dict(area="Etna · Alcantara Valley", title="Etna wine and the Alcantara gorge",
  before=[("si-cast2", "Castiglione di Sicilia on the north side of Etna"), ("am-alc1", "The Alcantara gorge")],
  prose=["Drive inland to the Alcantara valley and Castiglione di Sicilia, a medieval hill town on the north side of Etna, for a morning among castle ruins and a long Sicilian lunch. In the afternoon, taste volcanic wines with local cheeses at Tenuta di Fessina, among the vineyards below the volcano.",
         "On the way back, stop at the Gole dell'Alcantara, a gorge of basalt columns carved by the river through old lava. In summer, when the water is low and very cold, you can wade along the riverbed. Dinner is nearby before the drive back to Taormina."],
  after=[("si-etna", "Mount Etna at dawn")],
  tip="<b>Rent a car or hire a driver today.</b> None of these stops are practical by train or bus, and after the tasting someone shouldn't be driving."),
 dict(area="Taormina", title="The Greek theatre, a granita and the gardens",
  before=[("si-theatre1", "The Ancient Theatre of Taormina, with Etna beyond")],
  prose=["Get to the Teatro Antico when it opens, before the tour groups. The Greeks built it in the 3rd century BC and the Romans rebuilt it, and the view through its broken stage wall, down the coast to Etna, is one of the most famous in Italy.",
         "At midday, have a granita at Bam Bar, the best known in town, with a warm brioche to dip in it. Spend the early afternoon in the Villa Comunale, the hillside gardens laid out by Florence Trevelyan in the late 1800s, then a late lunch of pasta alla Norma at Osteria da Rita."],
  after=[("si-granita2", "Granita and brioche"), ("am-villa2", "In the Villa Comunale gardens")],
  edit="Add a sunset aperitivo on day 6"),
 dict(area="Taormina · Mazzarò", title="Isola Bella, then home",
  before=[("am-isola3", "Isola Bella and its sandbar from above"), ("am-isola2", "Isola Bella from the shore")],
  prose=["Breakfast at Wunderbar on Piazza IX Aprile, the terrace square with the best view in town. Then take the cable car down to Mazzarò and walk to Isola Bella, the little island joined to the beach by a sandbar. It's a nature reserve now, with a small museum in its old villa. Catania airport is about an hour away."]),
]

PRACTICAL = """
<h2>Getting around</h2>
<p><b>On the Amalfi Coast, use ferries and buses.</b> Ferries link Positano, Amalfi and Capri from spring to autumn, and SITA buses run along the coast road all year. Don't rent a car here: the road is narrow, parking is scarce and the views are wasted on the driver. <b>In Sicily, rent a car or hire a driver for day 5.</b> Taormina itself is best on foot, and its center is closed to most traffic.</p>
<p><b>Between the two:</b> fly from Naples to Catania. The flight is under an hour. Driving or taking the train takes most of a day.</p>
<h2>When to go</h2>
<p>May, June, September and early October have warm seas without August's crowds and prices. Many ferries, beach clubs and some hotels close from November to March.</p>
"""
FAQ = [
 ("Can you do the Amalfi Coast and Sicily in one week?", "Yes, with one base on each and a flight between them. Three nights in Positano covers Capri, Ravello and Amalfi, and three in Taormina covers the theatre, Etna and Isola Bella. The flight from Naples to Catania is under an hour."),
 ("How do you get from the Amalfi Coast to Sicily?", "Fly from Naples to Catania, then drive about an hour to Taormina. Allow about 90 minutes from Positano to Naples airport. Going by train or car takes most of a day."),
 ("How much does a week on the Amalfi Coast and in Sicily cost?", "Roamly estimates about {total} for two people on the ground, covering mid-range hotels, food, a private boat day, wine tasting and transfers. That's roughly {each} each, before flights."),
 ("Is Positano or Amalfi a better base?", "Positano is more dramatic and has good ferry links to Capri. Amalfi is more central for buses and for Ravello. For a short stay with a Capri day, Positano works well."),
]
