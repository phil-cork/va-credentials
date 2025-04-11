import marimo

__generated_with = "0.12.8"
app = marimo.App(width="medium")


@app.cell
def _():
    import marimo as mo
    import altair as alt
    import polars as pl
    return alt, mo, pl


@app.cell
def _(pl):
    all_programs = pl.read_excel("data/DownloadPrograms.xlsx")

    va_programs = all_programs.filter(pl.col('state')=="VA")
    return all_programs, va_programs


@app.cell
def _(alt, pl, va_programs):
    served_completed = alt.Chart(va_programs.filter( (pl.col('d120_total_served') >0) & (pl.col('d122_total_completed') > 0) )).mark_point().encode(
        x='d120_total_served',
        y='d122_total_completed',
        color='d104_entity_type',
    ).interactive()

    served_completed
    return (served_completed,)


@app.cell
def _(alt, va_programs):
    alt.Chart(va_programs).mark_circle().encode(
        alt.X(alt.repeat("column"), type='quantitative'),
        alt.Y(alt.repeat("row"), type='quantitative'),
        color='d104_entity_type:N'
    ).properties(
        width=150,
        height=150
    ).repeat(
        row=['d111_non_wioa_tuition_cost', 'd113_program_length_hours', 'c_completed_percent'],
        column=['c_completed_percent', 'd113_program_length_hours', 'd111_non_wioa_tuition_cost']
    ).interactive()
    return


@app.cell
def _(alt, pl, va_programs):
    alt.Chart(va_programs.filter( (pl.col('d113_program_length_hours') >0) & (pl.col('c_completed_percent') > 0) )).mark_point().encode(
        x='d113_program_length_hours',
        y='c_completed_percent',
        color='d104_entity_type',
    ).interactive()
    return


@app.cell
def _():
    return


if __name__ == "__main__":
    app.run()
