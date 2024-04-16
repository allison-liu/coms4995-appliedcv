"ArtEmis: Affective Language for Visual Art" 
	by P. Achlioptas, M. Ovsjanikov, K. Haydarov, M. Elhoseiny, L. Guibas


--------------------------------------------------------------------------------------------------------------------------------------------------------------------------
	This is a README file for the two datasets named "ArtEmis" (Art Emotions) and "OLA" (Objective Language for Art) which contain 454,684 and 5,000 annotations each.
--------------------------------------------------------------------------------------------------------------------------------------------------------------------------

A few words for ArtEmis:
	(1) the artemis_dataset_release_v0.csv has 454,684 rows and 5 rows: 	 
			'art_style', 'painting', 'emotion', 'utterance', 'repetition'

		in the standard format of the WikiArt dataset you can associate an artwork with our annotations by accessing you local directory like this: 
		<your-top-wiki-art-dir> / 'art_style' / 'painting'  + '.jpg'.

		the 'emotion' corresponds to the button clicked by the annotator out of the 9 options explained in the paper.

		the 'utterance' is the explanation given in support of that emotion.

		the 'repetition' is an integer noting how many annotators have provided an explanation for each artwork. On average this number is 5.68. However for 701 artworks we have asked more than 41 annotators to give their opinion. This set (denoted as "rest" in the official split) is useful to measure e.g., the effect the repetition has in metrics like BLEU etc.

	(2) we have found out that the commonly used WikiArt dataset that contains 81,466 artworks has some artworks doubly listed under different art-styles. In this official release of ArtEmis we have removed such duplicate artworks, resulting in affective annotations for 80,031 *unique* artworks.

	(3) some annotators reached out to us post-their submission time to correct/update their explanations; also we have done a fair amount of manual spell-checking. To update the utterances to reflect these changes & to create the train/test/val splits we used when training _any_ of our neural networks, please use the "preprocess_artemis_data.py" script available in https://github.com/optas/artemis.git


A few words about OLA:
	OLA was collected to be used by the "ANP-baseline" of the paper. Its corresponding ola_dataset_release_v0.csv contains 5,000 rows with objective/descriptive utterances for artworks of WikiArt which (ideally) should not reflect any affect or sentiment. 

	The columns 'art_style' & 'painting' can be used similarly to ArtEmis as described above.

	The column 'utterance' contains each underlying description.


Panos Achlioptas, on behalf of the ArtEmis team @ March 25, 2021.


The ArtEmis Team:
P. Achlioptas (Stanford)
M. Ovsjanikov (Ecole Polytechnique)
K. Haydarov (King Abdullah University of Science and Technology, KAUST)
M. Elhoseiny (King Abdullah University of Science and Technology, KAUST)
L. Guibas (Stanford)