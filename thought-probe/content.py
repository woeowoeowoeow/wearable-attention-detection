"""Content definitions for the thought probe reading study.

Edit PASSAGES to change reading passages and quiz questions without
modifying the main application logic. Add or remove passages as needed.

Each passage entry contains:
    - title: Display title for the passage
    - text: The full passage text displayed during reading (replace with
      your actual reading passages)
    - questions: List of 7 quiz question dicts, each with:
        - id: Unique question identifier (e.g., "A1", "A2")
        - question: The question text
        - options: List of 4 answer choices
        - correct_index: 0-based index of the correct answer in options
"""

QUESTIONNAIRE_ITEMS = [
    "Did you notice anything unusual during this session?",
    "How intrusive did the attention check-ins feel?",
    "How helpful did you find any feedback you received?",
    "Would you be willing to use a tool like this while studying "
    "independently?",
    "How well were you able to focus on the reading tasks?",
]

QUESTIONNAIRE_ITEM_LABELS = {
    1: "Not at all",
    2: "Slightly",
    3: "Moderately",
    4: "Very",
    5: "Extremely",
}

PASSAGES = {
    "A": {
        "title": "The Coral Reef Paradox",
        "text": (
            "Coral reefs cover less than one percent of the ocean floor, yet they "
            "support roughly a quarter of all marine species. This disproportionate "
            "relationship between physical footprint and ecological importance has "
            "long puzzled biologists, and the answer lies not in the coral itself, "
            "but in a partnership so fundamental that neither party can survive "
            "without the other.\n\n"
            "A coral polyp is a small, soft-bodied animal related to sea anemones "
            "and jellyfish. On its own, a polyp is an unremarkable organism, capable "
            "of capturing tiny food particles from the water but incapable of "
            "building the massive limestone structures that define a reef. The "
            "architecture of a reef comes from something else entirely: a "
            "microscopic algae called zooxanthellae that lives inside the coral's "
            "tissue.\n\n"
            "This algae performs photosynthesis, converting sunlight into sugars "
            "the way a plant does. Crucially, it shares the majority of this energy "
            "with its coral host, providing up to ninety percent of the polyp's "
            "nutritional needs. In exchange, the coral provides the algae with a "
            "protected home, a steady supply of carbon dioxide, and access to "
            "sunlight near the ocean's surface. This arrangement, called a "
            "symbiotic relationship, allows the coral to grow far larger and "
            "faster than it otherwise could, depositing calcium carbonate to "
            "build the skeletal structures that accumulate, generation after "
            "generation, into the reefs that shelter so much of the ocean's "
            "biodiversity.\n\n"
            "The relationship, however, is fragile. Zooxanthellae are remarkably "
            "sensitive to temperature. When ocean water warms by even one or two "
            "degrees Celsius above the normal seasonal maximum, the algae's "
            "photosynthetic machinery begins to malfunction, producing compounds "
            "that are toxic to the coral if allowed to accumulate. In response, "
            "the coral expels its algae, sometimes within a matter of days. "
            "Without the pigmented algae living in its tissue, the coral's white "
            "limestone skeleton becomes visible through its now-transparent "
            "flesh, a phenomenon known as coral bleaching.\n\n"
            "Bleaching is not immediately fatal. A coral can survive for weeks "
            "without its algae, and if the water cools back to a tolerable range, "
            "many corals will recruit new zooxanthellae and recover relatively "
            "quickly. The danger comes from prolonged or repeated thermal stress. "
            "A bleached coral, deprived of ninety percent of its food supply, "
            "begins to starve. If favorable conditions do not return within a few "
            "weeks to a couple of months, the coral dies, leaving behind a bare "
            "limestone skeleton that is rapidly colonized by algae and other "
            "organisms unable to support the dense web of life a living reef once "
            "hosted.\n\n"
            "The 2014 to 2017 global bleaching event, the longest and most "
            "widespread on record, affected reefs in every major ocean basin. "
            "Researchers surveying affected sites found that some reef systems "
            "lost more than half their coral cover within a single bleaching "
            "season. What made this event particularly alarming to scientists "
            "was not just its scale but its frequency. Mass bleaching events, "
            "once estimated to occur perhaps once every twenty-five to thirty "
            "years under natural climate variability, have begun occurring at "
            "intervals of five to six years as ocean temperatures have risen.\n\n"
            "This compression of the timeline between bleaching events matters "
            "because coral recovery is slow. Even under ideal conditions, a reef "
            "that has lost significant coral cover may take ten to fifteen years "
            "to rebuild comparable structure and biodiversity. If a second major "
            "bleaching event strikes before a reef has recovered from the first, "
            "the cumulative damage compounds, and the reef's capacity to recover "
            "diminishes with each successive shock. Some marine biologists have "
            "described this as a ratchet effect: each event pushes the system "
            "further from its baseline, and the intervals between events are no "
            "longer long enough to allow a full return to that baseline before "
            "the next disturbance arrives.\n\n"
            "Not all coral species respond identically to thermal stress, which "
            "has led researchers to investigate why certain colonies survive "
            "bleaching events that devastate their neighbors. Some coral species "
            "host multiple types of zooxanthellae simultaneously, and certain "
            "algal strains tolerate higher temperatures than others. A coral "
            "that happens to host a heat-tolerant strain, or that can shift its "
            "algal population toward more tolerant strains under stress, may "
            "bleach less severely or recover more readily than a genetically "
            "similar coral hosting only heat-sensitive algae. This discovery has "
            "prompted interest in selective breeding and even laboratory-assisted "
            "evolution of heat-tolerant algal strains, with the goal of seeding "
            "vulnerable reefs with corals more likely to withstand future "
            "warming.\n\n"
            "Such interventions remain experimental and limited in scale compared "
            "to the size of the reefs they would need to protect. Most "
            "researchers in the field are careful to frame these techniques as a "
            "means of buying time for particularly vulnerable or ecologically "
            "significant reef systems, not as a substitute for addressing the "
            "underlying rise in ocean temperatures. The relationship between "
            "coral and algae that built the most biodiverse ecosystems in the "
            "ocean is the same relationship now placing those ecosystems at "
            "risk, a fact that has reframed how marine biologists think about "
            "reef conservation: protecting the reef is inseparable from "
            "protecting the precise environmental conditions, narrow as they "
            "are, under which the partnership between coral and algae can "
            "continue."
        ),
        "questions": [
            {
                "id": "A1",
                "question": (
                    "According to the passage, what percentage of a coral "
                    "polyp's nutritional needs can be provided by zooxanthellae?"
                ),
                "options": [
                    "Up to fifty percent",
                    "Up to seventy-five percent",
                    "Up to ninety percent",
                    "Nearly one hundred percent",
                ],
                "correct_index": 2,
            },
            {
                "id": "A2",
                "question": (
                    "What does the coral provide to the zooxanthellae in their "
                    "symbiotic relationship?"
                ),
                "options": [
                    "Calcium carbonate for the algae to build its own skeleton",
                    "A protected home, carbon dioxide, and access to sunlight",
                    "Toxic compounds that the algae need to survive",
                    "A constant supply of small food particles",
                ],
                "correct_index": 1,
            },
            {
                "id": "A3",
                "question": (
                    "Based on the passage, what directly causes coral bleaching?"
                ),
                "options": [
                    "The coral actively choosing to expel the algae for no "
                    "environmental reason",
                    "The algae's photosynthetic process malfunctioning at "
                    "elevated temperatures and producing toxic compounds",
                    "A virus that infects and kills the zooxanthellae",
                    "The coral skeleton dissolving in warmer water",
                ],
                "correct_index": 1,
            },
            {
                "id": "A4",
                "question": (
                    "Why does the passage describe the increased frequency of "
                    "bleaching events as particularly alarming, rather than "
                    "just their scale?"
                ),
                "options": [
                    "Because frequent events leave no light visible through "
                    "the coral",
                    "Because reefs need ten to fifteen years to recover, and "
                    "shorter intervals between events prevent full recovery "
                    "before the next disturbance",
                    "Because more frequent events attract more tourists to "
                    "reef sites",
                    "Because frequency was not something scientists could "
                    "measure before 2014",
                ],
                "correct_index": 1,
            },
            {
                "id": "A5",
                "question": "What is the \"ratchet effect\" described in the passage?",
                "options": [
                    "A mechanical process used to harvest coral samples",
                    "The way coral physically locks itself to ocean floor "
                    "sediment",
                    "A pattern where each bleaching event pushes the reef "
                    "system further from its original baseline, with "
                    "insufficient time to fully recover before the next event",
                    "The seasonal cycle of algae leaving and returning to "
                    "host corals",
                ],
                "correct_index": 2,
            },
            {
                "id": "A6",
                "question": (
                    "Why might some coral colonies survive bleaching events "
                    "that devastate genetically similar neighboring colonies?"
                ),
                "options": [
                    "They are located in deeper, colder water exclusively",
                    "They host heat-tolerant strains of zooxanthellae or can "
                    "shift toward more tolerant algal populations under stress",
                    "They have thicker limestone skeletons that resist "
                    "temperature change",
                    "They reproduce more quickly than other coral species",
                ],
                "correct_index": 1,
            },
            {
                "id": "A7",
                "question": (
                    "How does the passage characterize current research into "
                    "selective breeding of heat-tolerant algae?"
                ),
                "options": [
                    "As a complete solution that has already been implemented "
                    "at scale across major reef systems",
                    "As an experimental approach intended to buy time for "
                    "vulnerable reefs, not a substitute for addressing rising "
                    "ocean temperatures",
                    "As a failed approach that researchers have largely "
                    "abandoned",
                    "As more important than reducing ocean temperatures",
                ],
                "correct_index": 1,
            },
        ],
    },
    "B": {
        "title": "The Unreliable Witness",
        "text": (
            "For most of the twentieth century, eyewitness testimony held a "
            "privileged place in courtrooms. A confident witness pointing to a "
            "defendant and stating \"that's the person I saw\" carried enormous "
            "persuasive weight with juries, often outweighing physical evidence "
            "or expert testimony to the contrary. This intuitive trust in "
            "eyewitness identification rested on a simple assumption: that human "
            "memory functions something like a video recording, capturing events "
            "as they happened and allowing for accurate playback when needed "
            "later.\n\n"
            "Decades of research in cognitive psychology have dismantled this "
            "assumption almost entirely. Memory, researchers have found, is not "
            "a passive recording device. It is a reconstructive process, one in "
            "which the brain rebuilds an approximation of a past event each time "
            "it is recalled, drawing on fragments of the original experience "
            "alongside expectations, assumptions, and information encountered "
            "after the event itself. This reconstructive quality makes memory "
            "remarkably useful for everyday reasoning, but it also makes it "
            "vulnerable to distortion in ways that have profound consequences in "
            "legal settings.\n\n"
            "One of the most well-documented sources of distortion is what "
            "psychologists call the misinformation effect. In a series of "
            "influential experiments beginning in the 1970s, researchers showed "
            "participants a sequence of events, such as a simulated car "
            "accident, and then asked questions that subtly introduced false "
            "information. A question asking \"how fast was the car going when "
            "it passed the barn\" might be posed even when no barn appeared in "
            "the original footage. A significant proportion of participants "
            "later reported having seen a barn that never existed, with many "
            "expressing genuine confidence in this false memory. The implanted "
            "detail did not feel different from an authentic one; subjectively, "
            "it was indistinguishable.\n\n"
            "This finding posed an unsettling implication for criminal "
            "investigations. If a detective questioning a witness inadvertently "
            "suggests a detail, perhaps by phrasing a question in a leading way "
            "or by describing a suspect's appearance before asking the witness "
            "to identify someone, the witness's subsequent memory of the event "
            "may incorporate that suggestion as though it had been part of the "
            "original experience. The witness is not lying. They genuinely "
            "believe, and will testify under oath, that they remember something "
            "their brain has, in effect, manufactured after the fact.\n\n"
            "Compounding this vulnerability is a separate and equally "
            "counterintuitive finding: the relationship between a witness's "
            "confidence and their accuracy is far weaker than most people "
            "assume. Jurors consistently report that a witness's apparent "
            "certainty is one of the strongest factors influencing whether they "
            "believe a given identification. Yet experimental studies "
            "repeatedly find that confidence and accuracy, while not entirely "
            "unrelated, diverge substantially under realistic conditions, "
            "particularly when the original viewing conditions were poor, when "
            "significant time has elapsed since the event, or when the witness "
            "has been repeatedly questioned about the event in the interim. A "
            "witness can become more confident over time even as the underlying "
            "memory grows less accurate, especially if they have rehearsed "
            "their account multiple times or received subtle social feedback "
            "suggesting their identification was correct.\n\n"
            "Police identification procedures have historically amplified "
            "rather than mitigated these vulnerabilities. The traditional "
            "lineup, in which a witness views several individuals "
            "simultaneously and is asked to identify the perpetrator, "
            "encourages relative judgment: the witness compares the available "
            "options to one another and selects whichever person looks most "
            "similar to their memory, even if that person is not the actual "
            "perpetrator and the true culprit is not present at all. "
            "Researchers have demonstrated that this relative judgment process "
            "can be reduced, though not eliminated, by presenting individuals "
            "sequentially rather than simultaneously, which encourages "
            "witnesses to compare each person against their memory of the "
            "event rather than against the other individuals being shown.\n\n"
            "The administrator of an identification procedure introduces a "
            "further complication. If the officer conducting a lineup knows "
            "which individual is the suspect, even unconscious cues, a slight "
            "change in tone, a longer pause, a subtle reaction, can signal to "
            "the witness which choice is expected. Double-blind procedures, in "
            "which neither the witness nor the administering officer knows the "
            "suspect's identity, eliminate this channel of influence entirely, "
            "though they remain logistically more demanding and are not "
            "universally adopted by law enforcement agencies.\n\n"
            "These findings have begun to reshape legal practice, though "
            "unevenly across jurisdictions. Some courts now permit expert "
            "testimony specifically addressing the limitations of eyewitness "
            "memory, allowing jurors to weigh an identification with "
            "appropriate caution rather than the unwarranted confidence the "
            "legal system once afforded it by default. Several countries and a "
            "growing number of individual jurisdictions have mandated "
            "double-blind, sequential identification procedures as standard "
            "practice. Yet eyewitness misidentification remains, by a wide "
            "margin, the single most common contributing factor in cases where "
            "individuals are later proven innocent through subsequent evidence, "
            "a statistic that underscores how far legal practice still lags "
            "behind what cognitive science has established about the "
            "fundamental unreliability of memory under the conditions in which "
            "eyewitnesses are typically asked to perform it."
        ),
        "questions": [
            {
                "id": "B1",
                "question": (
                    "According to the passage, how does memory actually "
                    "function, contrary to the popular assumption?"
                ),
                "options": [
                    "As an accurate recording device similar to video",
                    "As a reconstructive process that rebuilds an "
                    "approximation of past events using fragments and other "
                    "information",
                    "As a process that improves in accuracy each time an "
                    "event is recalled",
                    "As a system that cannot be influenced by outside "
                    "information",
                ],
                "correct_index": 1,
            },
            {
                "id": "B2",
                "question": (
                    "In the misinformation effect experiments described, what "
                    "happened when researchers asked about a barn that never "
                    "appeared in the original footage?"
                ),
                "options": [
                    "Almost no participants were affected by the false "
                    "suggestion",
                    "Participants became suspicious and refused to answer",
                    "A significant number of participants later reported "
                    "seeing the barn and expressed genuine confidence in "
                    "that false memory",
                    "Only participants with poor eyesight were affected",
                ],
                "correct_index": 2,
            },
            {
                "id": "B3",
                "question": (
                    "Why does the passage describe witnesses who incorporate "
                    "suggested details as not lying?"
                ),
                "options": [
                    "Because they are instructed by detectives to say "
                    "specific things",
                    "Because they genuinely believe the manufactured memory "
                    "is real, since it does not subjectively feel different "
                    "from an authentic memory",
                    "Because courts do not allow witnesses to be questioned "
                    "about accuracy",
                    "Because the legal system does not require witnesses to "
                    "tell the truth",
                ],
                "correct_index": 1,
            },
            {
                "id": "B4",
                "question": (
                    "What does the passage say about the relationship between "
                    "a witness's confidence and their accuracy?"
                ),
                "options": [
                    "They are almost perfectly correlated under all "
                    "conditions",
                    "Confidence and accuracy diverge substantially, "
                    "especially under poor viewing conditions, after "
                    "significant time has passed, or after repeated "
                    "questioning",
                    "Witnesses who are confident are always more accurate "
                    "than less confident witnesses",
                    "Confidence has no relationship to accuracy whatsoever "
                    "in any condition",
                ],
                "correct_index": 1,
            },
            {
                "id": "B5",
                "question": (
                    "How does a traditional simultaneous lineup encourage "
                    "inaccurate identification, according to the passage?"
                ),
                "options": [
                    "It allows witnesses to ask questions of the suspects "
                    "directly",
                    "It only shows photographs rather than real people",
                    "It encourages relative judgment, where witnesses select "
                    "whoever looks most similar to their memory among the "
                    "choices, even if the actual perpetrator is absent",
                    "It requires witnesses to wait several years before "
                    "making an identification",
                ],
                "correct_index": 2,
            },
            {
                "id": "B6",
                "question": (
                    "What problem do double-blind identification procedures "
                    "specifically address?"
                ),
                "options": [
                    "The possibility that the administering officer might "
                    "unconsciously signal the expected choice to the witness",
                    "The cost of conducting a lineup with multiple suspects",
                    "The witness's ability to remember details from the "
                    "original event",
                    "The legal requirement that all witnesses must be "
                    "questioned twice",
                ],
                "correct_index": 0,
            },
            {
                "id": "B7",
                "question": (
                    "According to the final paragraph, what is true about the "
                    "gap between cognitive science findings and actual legal "
                    "practice?"
                ),
                "options": [
                    "Legal practice has fully caught up with and exceeds what "
                    "cognitive science recommends",
                    "Eyewitness misidentification remains the most common "
                    "contributing factor in proven wrongful convictions, "
                    "despite scientific findings about memory's "
                    "unreliability",
                    "Cognitive science has found that legal practices were "
                    "never a problem to begin with",
                    "All jurisdictions have already adopted double-blind "
                    "sequential procedures universally",
                ],
                "correct_index": 1,
            },
        ],
    },
}