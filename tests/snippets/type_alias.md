# type_alias

## ReferenceGenome

```python
ReferenceGenome = Dict[str, SeqRecord]
```

## class SeqRecord

## align\_sequences()

calls the alignment tool and parses the return output for a set of sequences

```python
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
```

**Args**

- sequences (`Dict[str, str]`): dictionary of sequences by name
- input_bam_cache (`BamCache`): bam cache to be used as a template for reading the alignments
- reference_genome (`ReferenceGenome`): the reference genome
- aligner (`str`): the name of the aligner to be used
- aligner_reference (`str`): path to the aligner reference file
- aligner_output_file
- aligner_fa_input_file
- aligner_output_log
- blat_limit_top_aln
- blat_min_identity
- clean_files
