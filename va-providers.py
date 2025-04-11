import marimo

__generated_with = "0.12.8"
app = marimo.App(width="medium")


@app.cell(hide_code=True)
def _(mo):
    mo.md(
        """
        ## VA Top Training Programs & Providers

        This notebook investigates the [Training Provider Results dataset](https://www.trainingproviderresults.gov/#!/about) to better understand the landscape of the credentials provided by the included institutions, which entities served the most students across various industries, and which industries are supposed by available trainings.

        ### Imports and Data
        """
    )
    return


@app.cell
def _():
    import marimo as mo
    import polars as pl
    import altair as alt
    return alt, mo, pl


@app.cell
def _(pl):
    all_programs = pl.read_excel("data/DownloadPrograms.xlsx") \
    .with_columns(pl.col('d110_cip_code').cast(pl.String).alias("CIPCode"))
    return (all_programs,)


@app.cell
def _(pl):
    # pull in CIP Codes crosswalks to pull the 2-digit codes, not included in the TPR dataset
    cip_codes = pl.read_csv("data/CIPCode2020.csv")
    cip_codes = cip_codes.drop(['Action', 'TextChange', 'CIPDefinition', 'CrossReferences', 'Examples'])
    # drop str artifacts from CIP code columns
    cip_codes = cip_codes.with_columns([pl.col('CIPCode').str.replace('="', "").str.replace('"', ""),
                                       pl.col("CIPFamily").str.replace('="', "").str.replace('"', "")])
    return (cip_codes,)


@app.cell
def _(all_programs, cip_codes, pl):
    # keep on VA and join with broader CIP codes list
    va_programs = all_programs.filter(pl.col('state')=="VA")
    va_programs = va_programs.join(cip_codes, how="left", on="CIPCode")
    va_programs
    return (va_programs,)


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""### Describing Virginia's Training Program Landscape""")
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""In the TrainingProviderResults.gov dataset, there are 2,531 programs in the state of Virginia.""")
    return


@app.cell
def _(pl, va_programs):
    by_entity = va_programs.group_by(pl.col('d104_entity_type').alias('entity type')) \
     .agg([pl.count("d104_entity_type").alias("total")]) \
     .with_columns((pl.col('total') / pl.col('total').sum()*100).alias('percent').round(2)) \
     .sort(by=pl.col('total'), descending=True)

    by_entity
    return (by_entity,)


@app.cell(hide_code=True)
def _(mo):
    mo.md(
        """
        Those programs are categorized by eight different "entity types"

        - In Virginia, a vast majority of entity's offering professional training fit into the "Other" category, representing 84% of all entities.

        - Private-for-Private rank a distant second with almost 10% representation.

        - Higher Education, whether offering a Baccalaureate degree, an Associate's degree, or a Certificate of Completion, consist of a combined ~3% of entities.

        - Private Non-Profit entities count for almost 2%.

        - Public and National Apprenticeship are less than one percent each.
        """
    )
    return


@app.cell
def _(pl, va_programs):
    by_provider = va_programs.group_by(pl.col('d101_eligible_training_provider').alias('provider')) \
     .agg([pl.count("d101_eligible_training_provider").alias("total")]) \
     .with_columns((pl.col('total') / pl.col('total').sum()*100).alias('percent').round(2)) \
     .sort(by=pl.col('total'), descending=True)

    by_provider
    return (by_provider,)


@app.cell(hide_code=True)
def _(mo):
    mo.md(
        """
        There are 265 unique providers of training programs in Virginia.

        Among them, Community Colleges are the most frequent result, making up 14 of the 15 entities offering the most programs, each consisting of ~2% of the entire dataset.

        Virginia Community College System (VCCS) reports that there are 23 community colleges across 40 campuses.
        """
    )
    return


@app.cell
def _(pl, va_programs):
    vccs = va_programs.filter(pl.col('d101_eligible_training_provider').str.contains("Community College"))
    vccs
    return (vccs,)


@app.cell(hide_code=True)
def _(mo):
    mo.md(
        """
        Community Colleges make up 1,028 of the 2,351 programs in Virginia - almost 44%.

        24 community colleges appear in the dataset, with the additional entry being the Main Campus of Lord Fairfax CC.
        """
    )
    return


@app.cell
def _(pl, vccs):
    vccs.group_by(pl.col('d101_eligible_training_provider')).len().sort('len', descending=True)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(
        r"""
        ### By Potential Outcome

        According to ETA-9171, the following codes coorelate to the potential outcomes for a given program

        - 1 = Industry-Recognized Certificate or Certification
        - 2 = Certificate of Completion of an Apprenticeship
        - 3 = License Recognized by the State Involved or the Federal Government
        - 4 = Associate’s Degree
        - 5 = A program of study leading to a baccalaureate degree
        - 6 = IHE Certificate of Completion
        - 7 = Secondary School Diploma or Its Equivalent
        - 8 = Employment
        - 9 = Measureable Skill Gain Leading to a Credential
        - 0 = Measureable Skill Gain Leading to Employment
        """
    )
    return


@app.cell
def _(pl, vccs):
    vccs.group_by(pl.col('d108_program')).len().sort('len', descending=True)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(
        r"""
        Certificates and Ceritifications are the most prominent outcomes, representing 661 of the programs listed. An associate's degree is the second most common. These trends fit earlier observations - CDLs appearing as the instances with the most volume by student served and the healthcare industry - many of which offer Associates degrees in nursing - appearing in high volume when considering the available programs.

        Note: Many entries include codes beyond the 0-9 scale - is it possible these are multiple entries such that '169' is an instance of 1,6, and 9?
        """
    )
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""### By CIP Codes""")
    return


@app.cell
def _(cip_codes, pl, va_programs):
    # keep only the cip codes and titles for the two-digit level of aggregation
    cip_family = cip_codes.filter(pl.col("CIPFamily")==pl.col("CIPCode"))

    va_programs.group_by(pl.col('CIPFamily')) \
     .agg([pl.count("CIPFamily").alias("total_programs"),
           pl.sum('d120_total_served').alias('total_served')

          ]) \
     .with_columns((pl.col('total_programs') / pl.col('total_programs').sum()*100).alias('percent_programs').round(2), \
                  (pl.col('total_served') / pl.col('total_served').sum()*100).alias('percent_served').round(2)) \
     .sort(by=pl.col('total_programs'), descending=True).join(cip_family, on="CIPFamily", how="left").drop('CIPCode')
    return (cip_family,)


@app.cell(hide_code=True)
def _(mo):
    mo.md(
        r"""
        When aggregating to the highest level of categorizing programs into the industry they serve, we see Health Professions make up 25% of all programs, followed by Computer and Information Sciences at 18% and Business roles at 10%.

        When sorting by the volume of individuals served, it's no surprise to see Transportation surge to the top, representing 45% of the entire population in the dataset. Many of the other leaders by program count are in the top ten - health, business, computer science, engineering, precision production, construction, and mechanics and repair.

        The new additions are General Students and Education, representing 2.5% of the population each, though there are only 11 and 29 programs in the state, respectively. Culinary and Security, which appeared in the top ten by program volume, serve between 0.5% and 0.6% of the population, meaning between 62 and 117 individuals.

        Across both metrics, we can focus on those that dominate one or both categories - Transportation, Health, Business, CS/IT, Construction Trades, Mechanic and Repair, and Engineering, and Precision Production.
        """
    )
    return


@app.cell
def _(pl, va_programs):
    health_programs = va_programs.filter(pl.col("CIPFamily") == "51")
    cs_programs = va_programs.filter(pl.col("CIPFamily") == "11")
    business_programs = va_programs.filter(pl.col("CIPFamily") == "52")
    engineering_programs = va_programs.filter(pl.col("CIPFamily") == "15")
    mechanic_programs = va_programs.filter(pl.col("CIPFamily") == "47")
    construction_programs = va_programs.filter(pl.col("CIPFamily") == "46")
    precision_programs = va_programs.filter(pl.col("CIPFamily") == "48")
    transportation_programs = va_programs.filter(pl.col("CIPFamily") == "49")
    return (
        business_programs,
        construction_programs,
        cs_programs,
        engineering_programs,
        health_programs,
        mechanic_programs,
        precision_programs,
        transportation_programs,
    )


@app.cell(hide_code=True)
def _(mo):
    mo.md(
        r"""
        ## Which providers lead by students served in each of the top industries?

        ### Health Programs
        """
    )
    return


@app.cell
def _(health_programs, pl):
    health_programs.filter(pl.col('d120_total_served') >0).group_by('d101_eligible_training_provider').agg([ 
    pl.sum("d120_total_served").alias("total_served_health")]).sort('total_served_health', descending=True)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""### Computer Science / IT""")
    return


@app.cell
def _(cs_programs, pl):
    cs_programs.filter(pl.col('d120_total_served') >0).group_by('d101_eligible_training_provider').agg([ 
    pl.sum("d120_total_served").alias("total_served_cs")]).sort('total_served_cs', descending=True)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""### Business""")
    return


@app.cell
def _(business_programs, pl):
    business_programs.filter(pl.col('d120_total_served') >0).group_by('d101_eligible_training_provider').agg([ 
    pl.sum("d120_total_served").alias("total_served_business")]).sort('total_served_business', descending=True)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""### Engineering""")
    return


@app.cell
def _(engineering_programs, pl):
    engineering_programs.filter(pl.col('d120_total_served') >0).group_by('d101_eligible_training_provider').agg([ 
    pl.sum("d120_total_served").alias("total_served_engineering")]).sort('total_served_engineering', descending=True)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""### Mechanic/Repair""")
    return


@app.cell
def _(mechanic_programs, pl):
    mechanic_programs.filter(pl.col('d120_total_served') >0).group_by('d101_eligible_training_provider').agg([ 
    pl.sum("d120_total_served").alias("total_served_mechanic")]).sort('total_served_mechanic', descending=True)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""### Construction""")
    return


@app.cell
def _(construction_programs, pl):
    construction_programs.filter(pl.col('d120_total_served') >0).group_by('d101_eligible_training_provider').agg([ 
    pl.sum("d120_total_served").alias("total_served_construction")]).sort('total_served_construction', descending=True)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""### Precision Production""")
    return


@app.cell
def _(pl, precision_programs):
    precision_programs.filter(pl.col('d120_total_served') >0).group_by('d101_eligible_training_provider').agg([ 
    pl.sum("d120_total_served").alias("sum")]).sort('sum', descending=True)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""### Transportation""")
    return


@app.cell
def _(pl, transportation_programs):
    transportation_programs.filter(pl.col('d120_total_served') >0).group_by('d101_eligible_training_provider').agg([ 
    pl.sum("d120_total_served").alias("sum")]).sort('sum', descending=True)
    return


if __name__ == "__main__":
    app.run()
