# OracleAI: A sports trading analyst
Made for @0racleBets. Uses OpenAI to parse input and determine desired information, and OddsAPI to fetch live odds.
## General Info:
OracleAI does not have any specific syntax requirements, the information just needs to be in the message.

**Command format: /{command} {arguments}**
## Commands:
* /leagues: Gets a list of all available leagues
* /events {league}: Gets a list of all events for a given league
* /odds {league, teams, market}: gets the live odds for a specific market for a specific match
* /markets {league}: gets the available markets for a specific league
* /best {league, teams, market}: gets the best odds for a specific market for a specific match
* /scores {league, teams}: get the live scores for a given match from up to 3 days ago
* /predict {league, teams, market}: predicts the outcome of a given match in a given market
* /advice {league, market}: suggests a bet for a given market in a given league
* /arb {sport}: looks for available arbitrage opportunities in a given sport

## Error Handling:
If you are having trouble getting OracleAI to interpret your request, use standard english instead. For example, '/best spain france euros h2h' could be rewritten as '/best What are the best h2h odds for the spain vs france uefa euro game?'. 
