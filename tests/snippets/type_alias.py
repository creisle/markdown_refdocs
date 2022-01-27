from typing import Dict


class SeqRecord:
    pass

ReferenceGenome = Dict[str, SeqRecord]


def align_sequences(
    sequences: Dict[str, str],
    input_bam_cache,
    reference_genome: ReferenceGenome,
    aligner: str,
    aligner_reference: str,
    aligner_output_file='aligner_out.temp',
    aligner_fa_input_file='aligner_in.fa',
    aligner_output_log='aligner_out.log',
    blat_limit_top_aln=25,
    blat_min_identity=0.7,
    clean_files=True,
    **kwargs,
):
    """
    calls the alignment tool and parses the return output for a set of sequences

    Args:
        sequences: dictionary of sequences by name
        input_bam_cache (BamCache): bam cache to be used as a template for reading the alignments
        reference_genome: the reference genome
        aligner (SUPPORTED_ALIGNER): the name of the aligner to be used
        aligner_reference: path to the aligner reference file
    """
    pass
