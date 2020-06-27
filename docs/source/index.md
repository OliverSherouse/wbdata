# Welcome to wbdata's documentation\!

## What is wbdata?

Wbdata is a simple python interface to find and request information from the
World Bank's various databases, either as a dictionary containing full metadata
or as a [pandas](http://pandas.pydata.org) DataFrame. Currently, wbdata wraps
most of the [World Bank API](http://data.worldbank.org/developers/api-overview),
and also adds some convenience functions for searching and retrieving
information.

Wbdata was designed to be used either in a script or in a shell. In a shell,
wbdata assumes that the user will use most functions to look up the codes
necessary to retrieve the information he wants. To this end, the default in
shell mode for most functions is to simply print the id and human-readable name
of each item in question. In a script, the default is to return the entire
response from the World Bank converted to python objects.

All the functions that you need to get started are in the `wbdata` module.

Finally, it should be pointed out that wbdata is in the "release early" portion
of the "release early, release often" cycle, and the current test suite is
pretty perfunctory. You won't end up with the wrong data, but any irregularities
I haven't specifically encountered in the World Bank database have not been
dealt with.

## Installation

Wbdata is available on [PyPi](https://pypi.python.org/pypi/wbdata) which means
you can install using pip:

> pip install -U wbdata

You can also download or get the source from
[GitHub](http://github.com/OliverSherouse/wbdata).

## Detailed Documentation

  - [Wbdata library reference](wbdata_library.md)
  - [api module](api_module.md)
  - [fetcher module](fetcher_module.md)

## A Typical User Session

Let's say we want to find some data for the ease of doing business in some
well-off countries. I might start off by seeing what sources are available and
look promising:

``` ipython
In [1]: import wbdata                                                                 

In [2]: wbdata.get_source()                                                           
Out[2]: 
  id  name
----  --------------------------------------------------------------------
   1  Doing Business
   2  World Development Indicators
   3  Worldwide Governance Indicators
   5  Subnational Malnutrition Database
   6  International Debt Statistics
  11  Africa Development Indicators
  12  Education Statistics
  13  Enterprise Surveys
  14  Gender Statistics
  15  Global Economic Monitor
  16  Health Nutrition and Population Statistics
  18  IDA Results Measurement System
  19  Millennium Development Goals
  20  Quarterly Public Sector Debt
  22  Quarterly External Debt Statistics SDDS
  23  Quarterly External Debt Statistics GDDS
  24  Poverty and Equity
  25  Jobs
  27  Global Economic Prospects
  28  Global Financial Inclusion
  29  The Atlas of Social Protection: Indicators of Resilience and Equity
  30  Exporter Dynamics Database – Indicators at Country-Year Level
  31  Country Policy and Institutional Assessment
  32  Global Financial Development
  33  G20 Financial Inclusion Indicators
  34  Global Partnership for Education
  35  Sustainable Energy for All
  36  Statistical Capacity Indicators
  37  LAC Equity Lab
  38  Subnational Poverty
  39  Health Nutrition and Population Statistics by Wealth Quintile
  40  Population estimates and projections
  41  Country Partnership Strategy for India (FY2013 - 17)
  43  Adjusted Net Savings
  44  Readiness for Investment in Sustainable Energy
  45  Indonesia Database for Policy and Economic Research
  46  Sustainable Development Goals
  50  Subnational Population
  54  Joint External Debt Hub
  57  WDI Database Archives
  58  Universal Health Coverage
  59  Wealth Accounts
  60  Economic Fitness
  61  PPPs Regulatory Quality
  62  International Comparison Program (ICP) 2011
  63  Human Capital Index
  64  Worldwide Bureaucracy Indicators
  65  Health Equity and Financial Protection Indicators
  66  Logistics Performance Index
  67  PEFA 2011
  68  PEFA 2016
  69  Global Financial Inclusion and Consumer Protection Survey
  70  Economic Fitness 2
  71  International Comparison Program (ICP) 2005
  72  PEFA_Test
  73  Global Financial Inclusion and Consumer Protection Survey (Internal)
  75  Environment, Social and Governance (ESG) Data
  76  Remittance Prices Worldwide (Sending Countries)
  77  Remittance Prices Worldwide (Receiving Countries)
  78  ICP 2017
  79  PEFA_GRPFM

```

Well, that "Doing Business"---source 1---looks like a winner. Let's see what
we've got available to us there.

``` ipython

In [3]: wbdata.get_indicator(source=1)                                                
Out[3]: 
id                                                 name
-------------------------------------------------  ---------------------------------------------------------------------------------------------------------------
ENF.CONT.COEN.ATDR                                 Enforcing contracts: Alternative dispute resolution (0-3) (DB16-20 methodology)
ENF.CONT.COEN.ATFE.PR                              Enforcing contracts: Attorney fees (% of claim)
ENF.CONT.COEN.COST.ZS                              Enforcing contracts: Cost (% of claim)
ENF.CONT.COEN.COST.ZS.DFRN                         Enforcing contracts: Cost (% of claim) - Score
ENF.CONT.COEN.CSMG                                 Enforcing contracts: Case management (0-6) (DB16-20 methodology)
ENF.CONT.COEN.CTAU                                 Enforcing contracts: Court automation (0-4) (DB17-20 methodology)
ENF.CONT.COEN.CTFE.PR                              Enforcing contracts: Court fees (% of claim)
ENF.CONT.COEN.CTSP.DB16                            Enforcing contracts: Court structure and proceedings (0-5) (DB16 methodology)
ENF.CONT.COEN.CTSP.DB1719                          Enforcing contracts: Court structure and proceedings (0-5) (DB17-20 methodology)
ENF.CONT.COEN.DB0415.DFRN                          Enforcing contracts (DB04-15 methodology) - Score
ENF.CONT.COEN.DB16.DFRN                            Enforcing contracts (DB16 methodology) - Score
ENF.CONT.COEN.DB1719.DFRN                          Enforcing contracts (DB17-20 methodology) - Score
ENF.CONT.COEN.ENFE.PR                              Enforcing contracts: Enforcement fees (% of claim)
ENF.CONT.COEN.ENJU.DY                              Enforcing contracts: Enforcement of judgment (days)
ENF.CONT.COEN.FLSR.DY                              Enforcing contracts: Filing and service (days)
ENF.CONT.COEN.PROC.NO                              Enforcing contracts: Procedures (number)
ENF.CONT.COEN.PROC.NO.DFRN                         Enforcing contracts: Procedures (number) - Score
ENF.CONT.COEN.QUJP.DB16.DFRN                       Enforcing contracts: Quality of the judicial processes index (0-19) (DB17-20 methodology) - Score
ENF.CONT.COEN.QUJP.DB1719.DFRN                     Enforcing contracts: Quality of judicial processes index (0-19) (DB17-19 methodology) - Score
ENF.CONT.COEN.QUJP.XD                              Enforcing contracts: Quality of the judicial processes index (0-18) (DB17-20 methodology)
ENF.CONT.COEN.RK.DB19                              Rank: Enforcing contracts (1=most business-friendly regulations)
ENF.CONT.COEN.TRJU.DY                              Enforcing contracts: Trial and judgment (days)
ENF.CONT.DURS.DY                                   Enforcing contracts: Time (days)
ENF.CONT.DURS.DY.DFRN                              Enforcing contracts: Time (days) - Score
ENF.CONT.EC.QJPI                                   Enforcing contracts: Quality of judicial administration index (0-18) (DB17-19 methodology)
IC.BUS.EASE.DFRN.DB1014                            Global: Ease of doing business score (DB10-14 methodology)
IC.BUS.EASE.DFRN.DB15                              Ease of doing business score (DB15 methodology)
IC.BUS.EASE.DFRN.DB16                              Global: Ease of doing business score (DB15 methodology)
IC.BUS.EASE.DFRN.XQ.DB1719                         Global: Ease of doing business score (DB17-20 methodology)
IC.BUS.EASE.XQ                                     Ease of doing business index (1=most business-friendly regulations)
IC.CNST.LIR.XD.02.DB1619                           Dealing with construction permits: Liability and insurance regimes index (0-2) (DB16-20 methodology)
IC.CNST.PC.XD.04.DB1619                            Dealing with construction permits: Professional certifications index (0-4) (DB16-20 methodology)
IC.CNST.PRMT.BQCI.015.DB1619.DFRN                  Dealing with construction permits: Building quality control index (0-15) (DB16-20 methodology) - Score
IC.CNST.PRMT.COST.WRH.VAL                          Dealing with construction permits: Cost (% of Warehouse value)
[And more deleted for brevity]
```

Alrighty. There's a lot there. But let's say I'm in the early stages of
developing a question and go for the most general measure, which is the "Ease of
Doing Business Index" with the id "IC.BUS.EASE.XQ".

Now remember, we're only interested in high-income countries right now, because
we're elitist. So let's use one of the convenience search functions to figure
out the code for the United States so we don't have to wait for data from a
bunch of other countries:

``` ipython
In [4]: wbdata.search_countries('united')                                                                                                                                     
Out[4]: 
id    name
----  --------------------
ARE   United Arab Emirates
GBR   United Kingdom
USA   United States
```

"USA". Very creative. Thank you, World Bank. But in any case, let's get our
data:

``` ipython
In [5]: wbdata.get_data("IC.BUS.EASE.XQ", country="USA")
Out[5]: 
[{'indicator': {'id': 'IC.BUS.EASE.XQ',
   'value': 'Ease of doing business index (1=most business-friendly regulations)'},
  'country': {'id': 'US', 'value': 'United States'},
  'countryiso3code': 'USA',
  'date': '2019',
  'value': 6,
  'unit': '',
  'obs_status': '',
  'decimal': 0},
 {'indicator': {'id': 'IC.BUS.EASE.XQ',
   'value': 'Ease of doing business index (1=most business-friendly regulations)'},
  'country': {'id': 'US', 'value': 'United States'},
  'countryiso3code': 'USA',
  'date': '2018',
  'value': None,
  'unit': '',
  'obs_status': '',
  'decimal': 0},
 {'indicator': {'id': 'IC.BUS.EASE.XQ',
   'value': 'Ease of doing business index (1=most business-friendly regulations)'},
  'country': {'id': 'US', 'value': 'United States'},
  'countryiso3code': 'USA',
  'date': '2017',
  'value': None,
  'unit': '',
  'obs_status': '',
  'decimal': 0},

[And so on]
```

And that returns a big long list of dictionaries with all the relevant data and
metadata as organized by the World Bank. Now let's say we want to look at the
United Kingdom as well ("GBR", see above), and only for the years 2010-2011. We
can actually search using multiple countries and restrict the dates using
datetime objects. Here's what that would look like:

``` ipython
In [6]: import datetime 

In [7]: data_date = datetime.datetime(2010, 1, 1), datetime.datetime(2011, 1, 1)                                                                                             

In [8]: wbdata.get_data("IC.BUS.EASE.XQ", country=["USA", "GBR"], data_date=data_date)                                                                                       
Out[8]: 
[{'indicator': {'id': 'IC.BUS.EASE.XQ',
   'value': 'Ease of doing business index (1=most business-friendly regulations)'},
  'country': {'id': 'GB', 'value': 'United Kingdom'},
  'countryiso3code': 'GBR',
  'date': '2011',
  'value': None,
  'unit': '',
  'obs_status': '',
  'decimal': 0},
 {'indicator': {'id': 'IC.BUS.EASE.XQ',
   'value': 'Ease of doing business index (1=most business-friendly regulations)'},
  'country': {'id': 'GB', 'value': 'United Kingdom'},
  'countryiso3code': 'GBR',
  'date': '2010',
  'value': None,
  'unit': '',
  'obs_status': '',
  'decimal': 0},
 {'indicator': {'id': 'IC.BUS.EASE.XQ',
   'value': 'Ease of doing business index (1=most business-friendly regulations)'},
  'country': {'id': 'US', 'value': 'United States'},
  'countryiso3code': 'USA',
  'date': '2011',
  'value': None,
  'unit': '',
  'obs_status': '',
  'decimal': 0},
 {'indicator': {'id': 'IC.BUS.EASE.XQ',
   'value': 'Ease of doing business index (1=most business-friendly regulations)'},
  'country': {'id': 'US', 'value': 'United States'},
  'countryiso3code': 'USA',
  'date': '2010',
  'value': None,
  'unit': '',
  'obs_status': '',
  'decimal': 0}]

```

And we get another list of dictionaries, which we can parse any which way we
please.

So let's get a little bit more analytic. Let's say we want to fetch this same
indicator, but also GDP per capita and for all high-income countries. Let's find
the other indicator we want using another convenience search function:

``` ipython
In [9]: wbdata.search_indicators("gdp per capita")                                                                                                                           
Out[9]: 
id                          name
--------------------------  ----------------------------------------------------------------------------------------
6.0.GDPpc_constant          GDP per capita, PPP (constant 2011 international $)
FB.DPT.INSU.PC.ZS           Deposit insurance coverage (% of GDP per capita)
NV.AGR.PCAP.KD.ZG           Real agricultural GDP per capita growth rate (%)
NY.GDP.PCAP.CD              GDP per capita (current US$)
NY.GDP.PCAP.CN              GDP per capita (current LCU)
NY.GDP.PCAP.KD              GDP per capita (constant 2010 US$)
NY.GDP.PCAP.KD.ZG           GDP per capita growth (annual %)
NY.GDP.PCAP.KN              GDP per capita (constant LCU)
NY.GDP.PCAP.PP.CD           GDP per capita, PPP (current international $)
NY.GDP.PCAP.PP.KD           GDP per capita, PPP (constant 2017 international $)
NY.GDP.PCAP.PP.KD.87        GDP per capita, PPP (constant 1987 international $)
NY.GDP.PCAP.PP.KD.ZG        GDP per capita, PPP annual growth (%)
SE.XPD.PRIM.PC.ZS           Government expenditure per student, primary (% of GDP per capita)
SE.XPD.SECO.PC.ZS           Government expenditure per student, secondary (% of GDP per capita)
SE.XPD.TERT.PC.ZS           Government expenditure per student, tertiary (% of GDP per capita)
UIS.XUNIT.GDPCAP.02.FSGOV   Initial government funding per pre-primary student as a percentage of GDP per capita
UIS.XUNIT.GDPCAP.1.FSGOV    Initial government funding per primary student as a percentage of GDP per capita
UIS.XUNIT.GDPCAP.1.FSHH     Initial household funding per primary student as a percentage of GDP per capita
UIS.XUNIT.GDPCAP.2.FSGOV    Initial government funding per lower secondary student as a percentage of GDP per capita
UIS.XUNIT.GDPCAP.23.FSGOV   Initial government funding per secondary student as a percentage of GDP per capita
UIS.XUNIT.GDPCAP.23.FSHH    Initial household funding per secondary student as a percentage of GDP per capita
UIS.XUNIT.GDPCAP.3.FSGOV    Initial government funding per upper secondary student as a percentage of GDP per capita
UIS.XUNIT.GDPCAP.5T8.FSGOV  Initial government funding per tertiary student as a percentage of GDP per capita
UIS.XUNIT.GDPCAP.5T8.FSHH   Initial household funding per tertiary student as a percentage of GDP per capita
```

Like good economists, we'll use the one that seems most impressive: GDP per
capita at PPP in constant 2005 dollars, which has the id "NY.GDP.PCAP.PP.KD".
But what about using high-income countries?

``` ipython
In [10]: wbdata.get_incomelevel()                                                                                                                                             
Out[10]: 
id    value
----  -------------------
HIC   High income
INX   Not classified
LIC   Low income
LMC   Lower middle income
LMY   Low & middle income
MIC   Middle income
UMC   Upper middle income
```

Funtastic. Finally, let's make sure we get our data into a lovely merged pandas
DataFrame, suitable for analysis with that library, statsmodels, or whatever
else we'd like.

``` ipython
In [11]: countries = [i['id'] for i in wbdata.get_country(incomelevel='HIC')]                                                                                                 

In [12]: indicators = {"IC.BUS.EASE.XQ": "doing_business", "NY.GDP.PCAP.PP.KD": "gdppc"}         

In [13]: df = wbdata.get_dataframe(indicators, country=countries, convert_date=True)   

In [14]: df.describe()                                                                                                                                                         
Out[14]: 
       doing_business          gdppc
count       57.000000    1713.000000
mean        49.561404   39660.815372
std         37.568042   21052.599082
min          1.000000    9492.153507
25%         20.000000   25522.078578
50%         41.000000   35889.316248
75%         72.000000   48233.136498
max        145.000000  161938.749262

```

The `doing_business` variable is only available for 2018, and `gdppc` is only
available for prior years, so let's take the latest observation of each to get
the correlation.

``` ipython
In [15]: df = wbdata.get_dataframe(indicators, country=countries, convert_date=True)                                                                                          

In [16]: df.sort_index().groupby('country').last().corr()                                                                                                                     
Out[16]: 
                doing_business     gdppc
doing_business        1.000000 -0.393077
gdppc                -0.393077  1.000000
```

And, since lower scores on that indicator mean more business-friendly
regulations, that's exactly what we would expect. It goes without saying that we
can use our data now to do any other analysis required.
