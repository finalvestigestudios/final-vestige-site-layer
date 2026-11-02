"""Source data for the Emergency Kit and Go-Bag Planner (tool slug: kit-builder).

Edit this file, then regenerate the tool body from the repo root:
    python -I preparedness/content/tools/src/gen_kit_builder.py

Rules for every item:
  * Items come only from the official lists already verified for the Start Here cluster (see audit/start-here/claims.json).
  * No quantities except where a source gives one (water: CDC/Ready.gov baseline). Everything else says "enough for your household".
  * `why` is a short, factual reason. If it is our reasoning, prefix it with "Editor's note:".
  * `src` lists register ids cited with {{cite:...}} tokens by the generator.
  * Never add a product, brand, price or affiliate link.
"""

SCENARIOS = [
    # id, label, default checked, one-line help
    ("adults", "Adults", True, "Everyone in the household who is 18 or older."),
    ("children", "Children", False, "Toddlers through teens."),
    ("infants", "Infants (under 12 months)", False, "Babies who are fed formula, breast milk or both."),
    ("pregnant", "Someone is pregnant or nursing", False, ""),
    ("pets", "Pets", False, "Including service and support animals."),
    ("mobility", "Mobility limitations", False, "Wheelchair, walker, cane, or help with stairs."),
    ("sensory", "Hearing, vision or communication needs", False, ""),
    ("power", "Powered medical equipment or cold-stored medicine", False, "Select this only if it applies. The planner never asks which."),
    ("storage", "Limited storage space", False, ""),
    ("foot", "Might leave on foot or by transit", False, ""),
    ("car", "Might leave by car", False, ""),
    ("budget", "Preparing on a tight budget", False, ""),
]

# group id -> (title, intro, scenario that reveals it or None for always)
GROUPS = [
    ("core", "Everyone: the basic kit", "These items appear on the official basic lists for every household.", None),
    ("hazard", "Everyone: add if your hazards call for it", "These depend on where you live and what could happen there. Your local emergency management office can tell you which apply.", None),
    ("adults", "Adults", "", "adults"),
    ("children", "Children", "", "children"),
    ("infants", "Infants", "The CDC bases its infant list on how the baby is fed.", "infants"),
    ("pregnant", "Pregnancy and nursing", "", "pregnant"),
    ("pets", "Pets", "Ready.gov suggests two kits: a larger one for sheltering in place and a lightweight one for evacuating.", "pets"),
    ("mobility", "Mobility limitations", "", "mobility"),
    ("sensory", "Hearing, vision and communication", "", "sensory"),
    ("power", "Powered equipment and cold-stored medicine", "Questions for your clinician, pharmacist or equipment supplier come first. This page gives no instruction about any medicine or device.", "power"),
    ("storage", "Limited storage", "", "storage"),
    ("foot", "Leaving on foot or by transit", "", "foot"),
    ("car", "Leaving by car", "", "car"),
    ("budget", "On a tight budget", "", "budget"),
]

# (id, group, label, why, [src ids])
ITEMS = [
    # ---- core ----
    ("water", "core", "Bottled water for drinking, cooking and sanitation: at least 1 gallon per person per day, for at least 3 days", "The CDC's baseline, with 2 weeks as the goal if you can. FEMA says to keep commercially bottled water with your kit, not tap water. Use the {{link:water-planner|water planner}} for your household's number.", ["cdc-water-store", "ready-are-you-ready"]),
    ("food", "core", "Non-perishable food your household will actually eat, plus a manual can opener", "Ready.gov says to store at least a several-day supply and to choose foods your family will eat, remembering special diets.", ["start-ready-food"]),
    ("radio", "core", "Battery-powered or hand-crank radio with NOAA Weather Radio tone alert, and spare batteries", "On the official list. NOAA Weather Radio broadcasts official warnings around the clock, which helps if phone service or power fails.", ["start-ready-kit", "start-ready-alerts"]),
    ("light", "core", "Flashlight, spare batteries and a whistle to signal for help", "On the official list. Editor's note: test the light and match the batteries when you pack it, because dead or wrong-size batteries look fine in a drawer.", ["start-ready-kit"]),
    ("firstaid", "core", "First aid kit", "On the official list.", ["start-ready-kit"]),
    ("charger", "core", "Phone with chargers and a backup battery", "On the official list.", ["start-ready-kit"]),
    ("docs", "core", "Copies of insurance policies, identification and bank records, in a waterproof, portable container or saved electronically", "On the official list. FEMA suggests paper copies in a fire- and waterproof box or with someone you trust, and password-protected electronic copies.", ["start-ready-kit", "ready-are-you-ready"]),
    ("cash", "core", "A small amount of cash in small bills", "Ready.gov says ATMs and credit cards may not work in a disaster. No source gives a dollar figure; choose an amount your household can set aside.", ["start-ready-financial"]),
    ("sanit", "core", "Moist towelettes, garbage bags and plastic ties for personal sanitation", "On the official list.", ["start-ready-kit"]),
    ("hygiene", "core", "Soap, hand sanitizer and personal hygiene items", "On the official list.", ["start-ready-kit"]),
    ("warm", "core", "A sleeping bag or warm blanket for each person, a change of clothes for your climate, and sturdy shoes", "On the official list.", ["start-ready-kit"]),
    ("maps", "core", "Local maps", "On the official list. The CDC adds that you can download maps to a phone in case there is no power or internet.", ["start-ready-kit", "start-cdc-family-kit"]),
    ("meds-core", "core", "Prescription medicines and eyeglasses, kept to the amount your pharmacist or prescriber advises", "The sources do not agree on how many days to keep (several days, 1 week, 2 weeks, 30 days), so ask your pharmacist or prescriber what applies to you. Do not change how you take any medicine because of a checklist.", ["start-ready-kit", "start-cdc-pyh-prescriptions"]),
    ("otc", "core", "Non-prescription medicines such as pain relievers, anti-diarrhea medication, antacids or laxatives", "On the official list. Ask a pharmacist what suits your household, and never give an adult product to a child or infant without a clinician's direction.", ["start-ready-kit"]),
    # ---- hazard-dependent ----
    ("mask", "hazard", "Dust mask or fitted respirator, if smoke, dust or contaminated air is a hazard where you live", "Ready.gov lists a dust mask; FEMA's 2020 guide recommends several fit-tested N95 respirators. The sources differ, so check with local emergency management.", ["start-ready-kit", "ready-are-you-ready"]),
    ("sheeting", "hazard", "Plastic sheeting, scissors and duct tape, if officials may ask you to shelter in place", "On the official list. Whether and how to seal a room depends on the hazard; follow local officials rather than this checklist.", ["start-ready-kit"]),
    ("wrench", "hazard", "Wrench or pliers to turn off utilities, once you have learned how and when", "On the official list. FEMA says to shut off utilities before leaving only if your home is damaged and you are told to, and to learn how beforehand from a professional or your utility.", ["start-ready-kit", "ready-are-you-ready"]),
    ("matches", "hazard", "Matches in a waterproof container, and a fire extinguisher", "Both are on Ready.gov's additional-items list.", ["start-ready-kit"]),
    ("dishes", "hazard", "Paper cups, plates, paper towels and plastic utensils", "On the official list as mess kits and disposable tableware.", ["start-ready-kit"]),
    ("paper", "hazard", "Paper and pencil, and something to do", "On the official list, which includes activities for children.", ["start-ready-kit"]),
    # ---- adults ----
    ("work", "adults", "A smaller kit at work that covers at least 24 hours, including food, water, medicines and walking shoes", "Ready.gov and FEMA both suggest being prepared to shelter at work for at least 24 hours.", ["start-ready-kit", "ready-are-you-ready"]),
    ("adult-contacts", "adults", "A written list of emergency contacts, including your out-of-area contact", "FEMA and the CDC suggest one contact outside your area, reachable two ways. The {{link:reunification-plan|plan builder}} prints one.", ["ready-are-you-ready", "start-cdc-pyh-connected"]),
    # ---- children ----
    ("c-water", "children", "A water bottle sized for each child", "The CDC's list for young children includes an age-appropriate water bottle.", ["start-cdc-family-kit"]),
    ("c-snacks", "children", "Nutritious snacks", "On the CDC's list for young children.", ["start-cdc-family-kit"]),
    ("c-clothes", "children", "Extra clothes and shoes in the child's current size", "On the CDC's list. Editor's note: children outgrow things, so check sizes when you review the kit.", ["start-cdc-family-kit"]),
    ("c-activities", "children", "Transportable activities such as coloring supplies, books or games", "The CDC and Ready.gov both list them.", ["start-cdc-family-kit", "start-ready-kit"]),
    ("c-id", "children", "A durable emergency contact or ID tag on clothing or a backpack, or a wristband with the child's name and your contact information", "The CDC suggests both for young children.", ["start-cdc-family-kit"]),
    ("c-numbers", "children", "Names and phone numbers that older children have memorized", "The CDC suggests helping older children memorize important names and numbers.", ["start-cdc-family-kit"]),
    ("c-photo", "children", "A recent family photo, including one of everyone together", "The CDC says current ID photos can help with reunification.", ["start-cdc-family-kit"]),
    ("c-toddler", "children", "For toddlers: play yard or playpen, potty-training supplies and disposable feeding items", "On the CDC's list for ages 1 to 5.", ["start-cdc-family-kit"]),
    ("c-school", "children", "The school's or childcare's emergency and reunification plan, written down", "FEMA asks parents to find out how schools communicate in a crisis, shelter in place, evacuate and reunite families.", ["ready-are-you-ready"]),
    # ---- infants ----
    ("i-rtf", "infants", "If formula-feeding: ready-to-feed formula in single-serving cans or bottles", "The CDC calls ready-to-feed the safest formula option in an emergency because it needs no water and comes in sterile single-use containers.", ["start-cdc-infant-checklist"]),
    ("i-powder", "infants", "If you must use powdered formula: formula, a liquid measuring cup, a food-grade mixing container with a lid, bottled water, bottles and nipples", "Only if you can clean the items with safe water and soap. The CDC says to take extra care that powdered formula is not contaminated.", ["start-cdc-infant-checklist"]),
    ("i-milk", "infants", "If breastfeeding or pumping: disposable nursing pads, milk storage bags, a small cooler with ice packs, the pump and parts, cords and batteries, and a manual pump", "The CDC says reusable pads need laundering, so pack disposable ones, and that pump parts and storage bags should not be used if you cannot clean them.", ["start-cdc-infant-checklist"]),
    ("i-diaper", "infants", "A stocked diaper bag: diapers, wipes, diaper rash cream, baby wash and resealable bags for dirty diapers and clothes", "The CDC suggests at least one large pack of diapers and at least two packs of wipes.", ["start-cdc-infant-checklist"]),
    ("i-feed", "infants", "Disposable cups, bibs and spoons, burp rags, nonperishable baby food, and bottled water", "On the CDC's list.", ["start-cdc-infant-checklist"]),
    ("i-carry", "infants", "A baby carrier, extra clothes, at least two blankets, and a portable crib", "On the CDC's list.", ["start-cdc-infant-checklist"]),
    ("i-health", "infants", "A thermometer, and the baby's medical and vaccination records", "On the CDC's list.", ["start-cdc-infant-checklist"]),
    ("i-pain", "infants", "Ask your pediatrician which infant pain reliever to carry and what dose, if any, they advise for your baby, and write it down", "The CDC lists an infant pain reliever with acetaminophen but gives no dosing guidance. Dosing depends on age, weight and the product label. Do not give any medicine to an infant without direction from a pediatrician or other prescriber.", ["start-cdc-infant-checklist"]),
    ("i-check", "infants", "Check the infant items every month", "The CDC says babies grow quickly, so check that you have enough formula for the baby's current needs and replace formula that is expiring.", ["start-cdc-infant-checklist"]),
    # ---- pregnancy ----
    ("p-meds", "pregnant", "Prenatal vitamins and other medications your provider advises", "On the CDC's pregnancy list. Ask your provider.", ["start-cdc-family-kit"]),
    ("p-water", "pregnant", "Extra water", "The CDC says to consider storing more water than the basic baseline if you are pregnant or lactating.", ["start-cdc-family-kit"]),
    ("p-plan", "pregnant", "A plan made with your health care provider for where you will get prenatal care or deliver if the office or hospital is closed", "On the CDC's pregnancy list.", ["start-cdc-family-kit"]),
    ("p-birth", "pregnant", "Ask your provider whether, and what, birth supplies make sense for you", "The CDC's pregnancy list includes emergency birth supplies. This tool does not explain what they are for or how to use them. If labor starts or a birth seems close, call your local emergency number.", ["start-cdc-family-kit"]),
    ("p-snacks", "pregnant", "Nutritious snacks, and sanitary and hygiene supplies", "On the CDC's pregnancy list.", ["start-cdc-family-kit"]),
    # ---- pets ----
    ("pet-food", "pets", "Several days of food in an airtight, waterproof container, and a water bowl with several days of water", "Ready.gov gives no per-animal quantity; ask your veterinarian for a daily amount.", ["ready-pets"]),
    ("pet-med", "pets", "An extra supply of regular medicine in a waterproof container, and a first aid kit your veterinarian recommends", "On Ready.gov's list.", ["ready-pets"]),
    ("pet-id", "pets", "Collar with ID tag, a harness or leash and a backup, and copies of registration and documents (waterproof and electronic)", "On Ready.gov's list. Ready.gov and the CDC also recommend microchipping with current contact details, including an emergency contact outside your area.", ["ready-pets", "start-cdc-pyh-connected"]),
    ("pet-carrier", "pets", "A crate or sturdy carrier, ideally one for each pet, that your pet is used to", "Ready.gov suggests leaving the carrier out and open, with treats and a familiar blanket inside, so it is not strange in an emergency.", ["ready-pets"]),
    ("pet-san", "pets", "Litter and box if appropriate, newspapers, paper towels, trash bags, and household bleach for sanitation", "On Ready.gov's list.", ["ready-pets"]),
    ("pet-photo", "pets", "A photo of you with your pet, and familiar toys, treats or bedding", "Ready.gov says a photo helps document ownership if you are separated, and familiar items reduce stress.", ["ready-pets"]),
    ("pet-place", "pets", "A pet-friendly place to go, chosen in advance, and a neighbor or friend who can help (a buddy system)", "Ready.gov and FEMA say many public shelters and hotels do not allow pets, and that only service animals may be allowed in public shelters.", ["ready-pets", "start-ready-evacuation"]),
    # ---- mobility ----
    ("m-manual", "mobility", "If you use a power wheelchair: a lightweight manual chair as a backup, if possible, and people who know how to assemble and operate your chair", "Ready.gov's tips for people with a mobility disability.", ["start-ready-disability"]),
    ("m-battery", "mobility", "An extra battery for a power wheelchair or other battery-operated assistive device, kept charged", "Ready.gov says to find out what agencies or charities might help if you cannot afford one.", ["start-ready-disability"]),
    ("m-repair", "mobility", "A patch kit or sealant and an extra inner tube if tires are not puncture-proof, and a portable air pump", "On Ready.gov's list.", ["start-ready-disability"]),
    ("m-cushion", "mobility", "An extra seat cushion, if you use one to protect your skin or keep your balance", "On Ready.gov's list.", ["start-ready-disability"]),
    ("m-cane", "mobility", "An extra cane or walker, if you use one and can get the extra", "Ready.gov and the CDC both list it.", ["start-ready-disability", "start-cdc-disability-kit"]),
    ("m-info", "mobility", "A list of the style and serial number of your devices, with any special operating instructions, and where the equipment came from", "On Ready.gov's list.", ["start-ready-disability"]),
    ("m-transport", "mobility", "Arrangements for accessible transport, made in advance, and neighbors who can help you leave the building", "The CDC warns accessible transport may not be available in an emergency, so ask paratransit or local government in advance.", ["start-cdc-disability-evacuate", "start-ready-disability"]),
    # ---- sensory ----
    ("s-radio", "sensory", "Deaf or hard of hearing: weather radio with text display and flashing alert, extra hearing-aid batteries, pen and paper, and a battery lantern", "Ready.gov's tips for people who are deaf or hard of hearing. The lantern lets sign language and lip reading continue in the dark.", ["start-ready-disability"]),
    ("s-vision", "sensory", "Blind or low vision: Braille or large-print labels on supplies, and a list of supplies on a flash drive or as an audio file", "Ready.gov's tips for people who are blind or have low vision.", ["start-ready-disability"]),
    ("s-comm", "sensory", "Communication devices or laminated cards with phrases or pictures, and a note of the device's model and who paid for it", "Ready.gov's tips for people with a speech disability.", ["start-ready-disability"]),
    ("s-cards", "sensory", "A printed medical information card and a communication assistance card for first responders", "The HHS Administration for Community Living offers both as downloads.", ["start-acl-emergency"]),
    # ---- power ----
    ("w-list", "power", "A list of everything that relies on electricity, with a plan for batteries or other power", "Ready.gov says to inventory items that need electricity and plan for alternatives.", ["start-ready-power"]),
    ("w-doctor", "power", "A written plan from your doctor or supplier for keeping powered medical equipment running during an outage", "Ready.gov says to talk to your doctor or health care provider about this.", ["start-ready-disability", "start-ready-power"]),
    ("w-ask", "power", "Questions asked of your prescriber or pharmacist about each cold-stored medicine: how long it can stay warm, and what the replacement plan is", "Ready.gov says to find out how long medication can be stored at higher temperatures. FEMA's newer sheet says to call your doctor or pharmacist if you depend on a refrigerated medicine that has been at room temperature. Do not decide for yourself whether to use or discard a medicine.", ["start-ready-power", "start-fema-power-sheet"]),
    ("w-cooler", "power", "A cooler and chemical ice packs, if you have medicine that must be chilled", "The CDC and Ready.gov both list them. Ask your pharmacist how to use them for your medicine.", ["start-cdc-pyh-prescriptions", "start-ready-disability"]),
    ("w-priority", "power", "A request to your power provider to be listed for priority restoration, and a second place you could go", "Ready.gov suggests asking your power provider. No source promises a response from such a list.", ["start-ready-disability"]),
    # ---- storage ----
    ("st-one", "storage", "Pack everything into one or two easy-to-carry containers, such as plastic bins or a duffel bag, with items in airtight bags", "Ready.gov and FEMA's guide both describe this.", ["start-ready-kit", "ready-are-you-ready"]),
    ("st-order", "storage", "Start with water, then food, then light and a radio; add the rest over time", "Editor's note: if space is tight, three days of water is a sensible stopping point and nothing in the sources says you must store more. A larger supply can come from a second location.", ["cdc-water-store"]),
    ("st-first", "storage", "Put new items at the back and older ones in front, and keep canned food in a cool, dry place", "FEMA's guide and Ready.gov's maintenance advice.", ["ready-are-you-ready", "start-ready-kit"]),
    ("st-two", "storage", "Keep a small portable kit separate from the main supply", "The Ready.gov checklist recommends one full kit at home and smaller portable kits where you spend time.", ["start-ready-supply-list"]),
    # ---- foot ----
    ("f-bag", "foot", "A go-bag each person can carry, and everyone knows where it is and who is responsible for it", "Ready.gov says to prepare a go-bag for leaving on foot or public transportation. Editor's note: lift each bag, because the heaviest item is usually water.", ["start-ready-evacuation"]),
    ("f-shoes", "foot", "Sturdy shoes, long pants, long sleeves and a hat to wear when you leave", "Ready.gov's evacuation checklist.", ["start-ready-evacuation"]),
    ("f-route", "foot", "A route and a destination chosen in advance, and a second one in a different direction", "Ready.gov says to identify several places you could go and notes your evacuation route may be on foot.", ["start-ready-evacuation"]),
    # ---- car ----
    ("car-tank", "car", "A gas tank kept at least half full", "Ready.gov and FEMA say gas stations may be closed or unable to pump during power outages.", ["start-ready-evacuation", "ready-are-you-ready"]),
    ("car-kit", "car", "A car kit: jumper cables, flares or a reflective triangle, ice scraper, car phone charger, blanket, map, and cat litter or sand for traction", "Ready.gov's list of automobile extras.", ["start-ready-car"]),
    ("car-one", "car", "A plan to take one car per family, with your emergency kit inside", "FEMA and Ready.gov say one car per family reduces congestion.", ["start-ready-evacuation", "ready-are-you-ready"]),
    ("car-flood", "car", "A reminder not to drive into flooded areas", "Ready.gov: six inches of water can cause a vehicle to lose control, and a foot of water will float many cars.", ["start-ready-car"]),
    # ---- budget ----
    ("b-free", "budget", "Write a plan, sign up for local alerts, and use the free communication-plan form", "Ready.gov's low-cost list begins with these free steps.", ["start-ready-low-cost"]),
    ("b-own", "budget", "Gather what you already own into one place before buying anything", "Editor's note: flashlights, blankets, a can opener, first aid supplies and sturdy shoes are all on the official list and may already be in the house.", ["start-ready-kit"]),
    ("b-thrift", "budget", "Look for camping gear, tools and cookware at garage sales and thrift stores, and add older clothing that still fits", "Ready.gov's low-cost advice.", ["start-ready-low-cost"]),
    ("b-eat", "budget", "Buy a few extra shelf-stable items you already eat, and rotate them into normal meals", "Editor's note, resting on Ready.gov's rule to choose foods your family will eat.", ["start-ready-food"]),
    ("b-help", "budget", "Know what help exists after a declared disaster, and keep key documents together", "FEMA may provide help after a presidentially declared disaster; conditions change, so read FEMA's current page.", ["start-fema-housing"]),
]
