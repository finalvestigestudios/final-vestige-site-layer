# The Brain Scan That Learned the Person, Not the Trance
## What a new EEG study teaches us about suggestion, scientific proof and the promise of mind-training audio

**Status:** Final Vestige Studios — independent editorial draft, unpublished, 12 November 2026. **Not medical advice or a product endorsement.** Research citations were inspected at their public full-text/abstract pages; two 2026 papers are preprints and have not been established as peer reviewed.

A computer was shown recordings of brains. On one test, it seemed to recognize a mental category with 82 percent accuracy. When investigators changed one detail—whether the computer had seen other recordings from the same people before—much of that apparent power vanished.

This is the story of a study in hypnosis-related research. But it is also a warning about an everyday sleight of hand: a measurement that looks impressively precise can answer the wrong question. And the closer the subject comes to something you want to believe about your own mind, the easier that mistake is to miss.

### 1. A promising percentage, and the question hiding inside it

In October 2026, a team led by researchers in Poland posted two related manuscripts about machine-learning classification of EEG recordings collected during guided imagery or comparison conditions. Sixty-two male participants, divided into 32 controls and 30 participants in a guided-imagery/"Hypno" condition, wore dense-array EEG caps. The team collected approximately 20-minute recordings and extracted successive ten-second windows.

That method creates many snippets per participant. It also creates a trap. If snippets from one individual land on both sides of the training-test split, a classifier may learn recurring features of *that individual* instead of a stable pattern generalizable to new people. Test performance can then flatter the model.

The more broadly described paper reported a best single-window random-split accuracy of 0.82. It also reported a lower frontal-region mean accuracy of 0.646 under leave-one-subject-out evaluation, with an AUC of 0.692; a ten-window prefrontal ensemble reached a mean accuracy of 0.738. The companion region-specific analysis found that an occipital signal scoring approximately 0.721 under a window-level split fell to 0.453 accuracy with subject-independent testing. Those are results **within the researchers' reported dataset and modeling choices**—not clinically validated ability to diagnose hypnotizability, and certainly not a demonstration that consumer audio changes the brain.

Sources: Wrobel et al., *EEG-Based Classification of Hypnotic Susceptibility Using Two-Dimensional Convolutional Neural Networks*, posted October 20, 2026: https://arxiv.org/abs/2610.27738 ; Wrobel & Wojcik, *Region-Specific EEG Classification of Hypnotic Susceptibility Using a Sliding-Window 2D CNN*, posted October 20, 2026: https://arxiv.org/abs/2610.28427 .

### 2. A person can accidentally become the answer key

Imagine showing a model 100 small handwriting samples from twelve writers. You label every piece written by six of them "rested" and every piece written by the other six "tired." Then you distribute the snippets at random between training and test sets. The model performs very well. Did it learn fatigue? Perhaps. But perhaps it simply learned which person's handwriting belonged to which label.

The fairer question is whether the model works on *writers it has never encountered*. That test removes the shortcut. The analogy is not a description of the EEG researchers' exact model: it isolates the logic of subject-wise separation.

EEG offers a particularly strong reminder because recordings can contain participant-specific information unrelated to the hypothesis. Noise, movement, stable anatomical and physiological differences, recording sessions and task conditions may all matter. Separating people at evaluation time reduces one central leakage risk, although it does not by itself remove every possible confound.

The 2026 team explicitly recognized this issue, which is why its subject-independent comparison is more illuminating than the most flattering number in the abstract. One region's performance collapsed toward chance. Other regions retained some above-chance reported performance. The appropriate interpretation is neither "EEG can read minds" nor "the entire project is worthless." It is that generalization needs to be tested under the conditions for which it is claimed.

### 3. What, exactly, were they classifying?

The titles use the language of "hypnotic susceptibility." Yet their dataset is described in terms of control and guided-imagery/Hypno groups. A reader must not silently convert that description into a commercially useful claim that a model identified individual responsiveness to any hypnosis recording, across ages, sexes, devices and everyday environments.

A scale of hypnotizability, a state induced during a guided exercise, an EEG pattern and a reported change in behavior are different things. Each might be interesting; none is interchangeable with the others. A study designed to separate experimental conditions cannot automatically establish a person's lifelong responsiveness to a suggestion. Nor does a model's classification accuracy show that a purchased audio file has caused a useful outcome.

The sample also restricts the scope of inference. Sixty-two men in a defined recording arrangement are not a population-level validation cohort. Different equipment, participants, ages, recording sites, expectations and independent prospective replications would be needed before discussing robust general use. Preprints can make useful science available quickly. They do not guarantee that the methods and conclusions have survived external review.

This matters because there are two questions that internet marketing often blends together: Can an intervention alter a laboratory measure? And does *this exact product* reliably improve a consumer's life in the way advertised? The first, even when answered convincingly, does not settle the second.

### 4. Suggestion is real as a subject of study. Its explanation is not settled.

Hypnosis research does not disappear because one classifier was overoptimistic. In a 2024 systematic review, Zahedi, Lynn and Sommer compared major theories of how hypnotic suggestions can influence perception, action and reported agency. Their conclusion was not that hypnosis is fiction. It was that competing accounts explain different parts of the evidence and that the mechanisms remain contested.

A separate 2024 review surveyed brain imaging and EEG studies of hypnosis and hypnotizability. Those approaches describe associations and experimental findings, with important methodological variability. They do not offer a single EEG signature that proves a consumer has entered a superior cognitive state.

Another 2023 scoping review noted that individual differences in responsiveness to suggestions, including those without a formal induction, are part of the research picture. It emphasizes context, traits and the interpretive difficulty of explaining complex experiences by a simple physiological switch.

Sources: Zahedi, Lynn & Sommer (2024), *How hypnotic suggestions work*, https://pubmed.ncbi.nlm.nih.gov/39032268/ ; De Pascalis (2024), *Brain Functional Correlates of Resting Hypnosis and Hypnotizability*, https://pubmed.ncbi.nlm.nih.gov/38391691/ ; Malloggi & Santarcangelo (2023), *Physiological Correlates of Hypnotizability*, https://www.mdpi.com/2076-3425/13/12/1632 .

### 5. The older story: an investigator who wanted the testimony to count

More than two centuries earlier, the Marquis de Puységur tried to build a record of experiences that he attributed to animal magnetism. The surviving memoirs assembled utterances, witnesses, repeated procedures, apparent predictions and failed cases. For modern readers, the material is valuable not because it proves a magnetic fluid, but because it exposes the mechanics of observation and interpretation.

Final Vestige's public **Puységur's Animal Magnetism Files** treats the 1785 original-edition reference separately from the 1813 working scan. It preserves contradictions, translation uncertainty and unfavorable outcomes, rather than promoting them away. One recurring issue is what a historical observer believed a strange experience could demonstrate.

The 1784 Franklin commission tackled an earlier animal-magnetism claim from a different angle. Blindfolded and otherwise controlled observations challenged the proposed physical "fluid." The commissioners did not show that subjects felt nothing. They tested a mechanism and found the evidence for it wanting. Our published Mesmerism investigation explains the limits of that inquiry, including its short observation period and the fact that the practice under examination was Deslon's.

The resonance with a modern machine-learning test is methodological, not supernatural. A witness can correctly report an experience yet misidentify its cause. A classifier can correctly detect statistical regularities yet answer a question different from the one advertised. Honest research asks which conclusion the observation actually licenses.

Primary Final Vestige source trails: https://finalvestige.com/free-resources/puysegurs-animal-magnetism-files/ and https://finalvestige.com/2026/11/02/mesmerism/ .

### 6. A twelve-minute field test you can actually use

A consumer need not buy brainwave software to learn something useful about their attention. This short observation exercise does **not** test hypnotizability, diagnose attention problems or reproduce an EEG experiment. It simply generates a record you can inspect.

**Minutes 0–2.** Pick one routine task that is safe to do seated, such as outlining a paragraph. Write what would count as finishing. Put your phone where you will not handle it, but do not change any safety-critical notification arrangement.

**Minutes 2–5.** Work without adding audio. Make a tally mark whenever you notice your mind wandering. Do not penalize yourself for the tally; noticing is the data.

**Minutes 5–8.** Pause and notice how accurately you can describe what you just did. Was your prediction about how long the task would take correct? Distinguish what you observed from the story you are telling about why it happened.

**Minutes 8–11.** Return to the same kind of task for another three minutes with a self-chosen, ordinary cue ("back to this line"). Record the number of completed lines or steps. Do not pretend that two tiny blocks constitute an experiment proving an intervention.

**Minute 12.** Write one observation, one alternative explanation, and one question for another day. Example: "I wrote more after the pause; perhaps I already knew the task better. I'd need repeated, counterbalanced sessions to judge a pattern."

This is not a treatment. Stop if uncomfortable. The exercise is free because the useful part is the distinction between a feeling of greater focus and an observable outcome.

### 7. What this has to do with buying meditation and hypnosis audio

Inspire3 markets **Zen12** as a twelve-minute meditation-audio program, **Hypnosis Live** as self-hypnosis downloads and **Brainwave Shots** as short recordings aimed at specific mental states. These are **seller descriptions**, not findings derived from the EEG manuscripts. Zen12's main page claims that a twelve-minute session yields the benefit of a much longer meditation period. That equivalence has not been established by the research evaluated here.

For a buyer concerned about time and routine, the legitimate value proposition is narrower. A structured set of short recordings may be more convenient than assembling your own listening program. Whether the sound, routine, expectation or repetition benefits a particular user is a different question. The publicly described **Zen12 Premium** package is the full twelve-level, 48-MP3 offer. The Beginner and Advanced variants are each six levels and 24 MP3s, serving different stages; none should be mislabeled as the complete twelve-level set.

Hypnosis Live's **Total Focus** is described by its seller as one 33-minute, 47 MB downloadable session. Brainwave Shots' **Focus Shot** advertises fifteen- and thirty-minute versions. The exact seller pages should be checked again at checkout; displayed promotions and refund policies may change or carry conditions. Neither format nor a positive testimonial is proof of a specific attention benefit.

Official products: https://inspire3.com/ ; https://zen12.com/ ; https://hypnosislive.com/mental-skills/total-focus ; https://brainwaveshots.com/focus-shot .

The FTC's endorsement guidance expects material commercial relationships to be obvious near recommendations, and its health-product guidance requires appropriate substantiation for objective benefits. This article is not a paid recommendation. If a vetted affiliate product link is ever activated, it must carry an adjacent clear disclosure. No existing author or researcher is represented as endorsing Zen12.

### 8. A better test of a claim

Before accepting a marketing promise about the mind, write down four separate questions. What was measured? Who was measured? What was the comparison? Does the evidence concern this exact product?

The new EEG manuscripts are a vivid lesson in why those questions matter. Their most instructive feature is not the high first-pass number. It is the experiment that made some of that number evaporate.

The heart of Final Vestige's work is to preserve the inconvenient second test. No wonder we need it as much when the subject is our own brain as when it is a century-old file in an archive.

**Research and editorial limits:** These 2026 papers are preprints. The above summaries are not a full external methodological replication. A classifier's accuracy is not an efficacy test; a guided-imagery contrast is not a consumer hypnosis trial; and historical records of claimed magnetism are not medical evidence. This page does not imply endorsement of any product or an authenticated affiliate relationship. No merchant links are activated.

**Further source record and reader paths:** Published change-blindness investigation https://finalvestige.com/2026/11/02/change-blindness/ ; published Puységur Files https://finalvestige.com/free-resources/puysegurs-animal-magnetism-files/ ; existing free Focus Fieldbook https://finalvestige.com/focus/ .