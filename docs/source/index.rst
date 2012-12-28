.. wbdata documentation master file, created by
   sphinx-quickstart on Sat Sep  1 20:11:30 2012.
   You can adapt this file completely to your liking, but it should at least
   contain the root `toctree` directive.

Welcome to wbdata's documentation!
==================================
What is wbdata?
---------------
Wbdata is a simple python interface to find and request information from the
World Bank's various databases, either as a dictionary containing full metadata
or as a `pandas <http://pandas.pydata.org>`_ DataFrame.  Currently, wbdata
wraps most of the `World Bank API
<http://data.worldbank.org/developers/api-overview>`_, and also adds some
convenience functions for searching and retrieving information.

Wbdata was designed to be used either in a script or in a shell.  In a shell,
wbdata assumes that the user will use most functions to look up the codes
necessary to retrieve the information he wants. To this end, the default in
shell mode for most functions is to simply print the id and human-readable name
of each item in question.  In a script, the default is to return the entire
response from the World Bank converted to python objects.

All the functions that you need to get started are in the :doc:`wbdata` module.

Finally, it should be pointed out that wbdata is in the "release early" portion
of the "release early, release often" cycle, and the current test suite is
pretty perfunctory.  You won't end up with the wrong data, but any
irregularities I haven't specifically encountered in the World Bank database
have not been dealt with.

Full Package Documentation
--------------------------
.. toctree::
    :maxdepth: 2

    wbdata
    fetcher

A Typical User Session
----------------------
Let's say we want to find some data for the ease of doing business in some
well-off countries.  I might start off by seeing what sources are available and
look promising:

    >>> wbdata.get_source()
    11	Africa Development Indicators
    31	Country Policy and Institutional Assessment (CPIA) 
    26	Corporate Scorecard
    1 	Doing Business
    30	Exporter Dynamics Database: Country-Year
    12	Education Statistics
    13	Enterprise Surveys
    28	Global Findex ( Global Financial Inclusion database)
    33	G20 Basic Set of Financial Inclusion Indicators
    14	Gender Statistics
    15	Global Economic Monitor
    27	GEP Economic Prospects
    32	Global Financial Development
    21	Global Economic Monitor (GEM) Commodities
    29	Global Social Protection
    16	Health Nutrition and Population Statistics
    18	International Development Association - Results Measurement System
    6 	International Debt Statistics
    25	Jobs for Knowledge Platform
    19	Millennium Development Goals
    24	Povstats
    20	Public Sector Debt
    23	Quarterly External Debt Statistics (QEDS) - General Data Dissemination System (GDDS)
    22	Quarterly External Debt Statistics (QEDS) - Special Data Dissemination Standard (SDDS)
    2 	World Development Indicators
    3 	Worldwide Governance Indicators

Well, that "Doing Business"---source 1---looks like a winner.  Let's see what
we've got available to us there.

    >>> wbdata.get_indicator(source=1)
    IC.BUS.EASE.XQ   	Ease of doing business index (1=most business-friendly regulations)
    IC.CRD.INFO.XQ   	Credit depth of information index (0=low to 6=high)
    IC.CRD.PRVT.ZS   	Private credit bureau coverage (% of adults)
    IC.CRD.PUBL.ZS   	Public credit registry coverage (% of adults)
    IC.DCP.COST      	Cost to build a warehouse (% of income per capita)
    IC.DCP.PROC      	Procedures required to build a warehouse (number)
    IC.DCP.TIME      	Time required to build a warehouse (days)
    IC.EC.COST       	Cost to enforce a contract (% of claim) 
    IC.EC.PROC       	Procedures required to enforce a contract (number)
    IC.EC.TIME       	Time required to enforce a contract (days)
    IC.EXP.COST.EXP  	Trade: Cost to export (US$ per container)
    IC.EXP.COST.IMP  	Trade: Cost to import (US$ per container)
    IC.EXP.DOCS      	Documents to export (number)
    IC.EXP.DOCS.IMP  	Trade: Documents to import (number)
    IC.EXP.TIME.EXP  	Trade: Time to export (day)
    IC.EXP.TIME.IMP  	Trade: Time to import (days)
    IC.GE.COST       	Cost to get electricity(% of income per capita)
    IC.GE.NUM        	Procedures required to connect to electricity (number)
    IC.GE.TIME       	Time required to connect to electricity (days)
    IC.IMP.DOCS      	Documents to import (number)
    IC.ISV.COST      	Resolving insolvency: cost (% of estate)
    IC.ISV.DURS      	Time to resolve insolvency (years)
    IC.ISV.RECRT     	Resolving insolvency: recovery rate (cents on the dollar)
    IC.LGL.CRED.XQ   	Strength of legal rights index (0=weak to 10=strong)
    IC.LIC.NUM       	Procedures required to build a warehouse (number)
    IC.LIC.TIME      	Time required to build a warehouse (days)
    IC.PI.DIR        	Extent of director liability index (0 to 10)
    IC.PI.DISCL      	Extent of disclosure index (0 to 10)
    IC.PI.INV        	Strength of investor protection index (0 to 10)
    IC.PI.SHAR       	Ease of shareholder suits index (0 to 10) 
    IC.REG.CAP       	Minimum paid-in capital required to start a business (% of income per capita)
    IC.REG.COST      	Cost to start a business (% of income per capita)
    IC.REG.DURS      	Time required to start a business (days)
    IC.REG.PROC      	Start-up procedures to register a business (number)
    IC.RP.COST       	Cost to register property (% of property value)
    IC.RP.PROC       	Procedures required to register property (number)
    IC.RP.TIME       	Time required to register property (days)
    IC.TAX.DURS      	Time to prepare and pay taxes (hours)
    IC.TAX.PAYM      	Tax payments (number)
    IC.TAX.TOTL.CP.ZS	Total tax rate (% of commercial profits)

Alrighty.  There's a lot there.  But let's say I'm in the early stages of
developing a question and go for the most general measure, which is the first
one, the "Ease of Doing Business Index", which has the id "IC.BUS.EASE.XQ".

Now remember, we're only interested in high-income countries right now, because
we're elitist.  So let's use one of the convenience search functions to figure
out the code for the United States so we don't have to wait for data from a
bunch of other countries:

    >>> wbdata.search_countries("united")
    ARE	United Arab Emirates
    GBR	United Kingdom
    USA	United States

"USA". Very creative.  Thank you, World Bank.  But in any case, let's get our
data:

    >>> wbdata.get_data("IC.BUS.EASE.XQ", country=USA)

And that will return a big long list of dictionaries with all the relevant
data and metadata as organized by the World Bank.  Now let's say we want to
look at the United Kingdom as well ("GBR", see above), and only for the years
2010-2011.  We can actually search using multiple countries and restrict the
dates using datetime objects. Here's what that would look like:

    >>> data_date = (datetime.datetime(2010, 1, 1), datetime.datetime(2011, 1, 1))
    >>> wbdata.get_data("IC.BUS.EASE.XQ", country=("USA", "GBR"), data_date=data_date)

And we get another long list of dictionaries, which we can parse any which way
we please.

So let's get a little bit more econometric. Let's say we want to fetch this
same indicator, but also gdp per capita and for all OECD countries.  Let's find
the other indicator we want using another convenience search function:

    >>> wbdata.search_indicators("gdp per capita")
    GDPPCKD             	GDP per Capita, constant US$, millions
    GDPPCKN             	Real GDP per Capita (real local currency units, various base years)
    NV.AGR.PCAP.KD.ZG   	Real agricultural GDP per capita growth rate (%)
    NY.GDP.PCAP.CD      	GDP per capita (current US$)
    NY.GDP.PCAP.KD      	GDP per capita (constant 2000 US$)
    NY.GDP.PCAP.KD.ZG   	GDP per capita growth (annual %)
    NY.GDP.PCAP.KN      	GDP per capita (constant LCU)
    NY.GDP.PCAP.PP.CD   	GDP per capita, PPP (current international $)
    NY.GDP.PCAP.PP.KD   	GDP per capita, PPP (constant 2005 international $)
    NY.GDP.PCAP.PP.KD.ZG	GDP per capita, PPP annual growth (%)
    SE.XPD.PRIM.PC.ZS   	Expenditure per student, primary (% of GDP per capita)
    SE.XPD.SECO.PC.ZS   	Expenditure per student, secondary (% of GDP per capita)
    SE.XPD.TERT.PC.ZS   	Expenditure per student, tertiary (% of GDP per capita)

Like good economists, we'll use the one that seems most impressive: GDP per
Capita at PPP in constant 2005 dollars, which has the id "NY.GDP.PCAP.PP.KD".
But what about using OECD countries?

    >>> wbdata.get_incomelevel()
    HIC	High income
    HPC	Heavily indebted poor countries (HIPC)
    INX	Not classified
    LIC	Low income
    LMC	Lower middle income
    LMY	Low & middle income
    MIC	Middle income
    NOC	High income: nonOECD
    OEC	High income: OECD
    UMC	Upper middle income

Funtastic.  Finally, let's make sure we get our data into a lovely merged
pandas DataFrame, suitable for analysis with that library, statsmodels, or
whatever else we'd like.

    >>> countries = [i['id'] for i in wbdata.get_country(incomelevel="OEC", display=False)]
    >>> indicators = {"IC.BUS.EASE.XQ": "doing_business", "NY.GDP.PCAP.PP.KD": "gdppc"}
    >>> df = wbdata.get_dataframe(indicators, country=countries, convert_date=True)
    >>> df.describe()
                gdppc  doing_business
    count    943.000000       62.000000
    mean   25394.219689       29.322581
    std     9495.732499       21.946861
    min     5543.572247        3.000000
    25%    19278.418595       11.000000
    50%    24640.540261       27.500000
    75%    30655.760574       41.000000
    max    74021.456759       89.000000
    >>> df = df.dropna()
    >>> df.gdppc.corr(df.doing_business)
    -0.2858022507189249

And, since lower scores on that indicator mean more business-friendly
regulations, that's exactly what we would expect. It goes without saying that
we can use our data now to do any other analysis required.

Indices and tables
==================

* :ref:`genindex`
* :ref:`modindex`
* :ref:`search`

