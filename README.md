legoktm/wikidata
============================

A collection of scripts assisting with the creation and upkeep of [wikidata.org](https://www.wikidata.org).

###Dependencies

- [legoktm/pywikipedia-rewrite/wikidata](https://github.com/legoktm/pywikipedia-rewrite/tree/wikidata) - Pywikipediabot rewrite branch fork, enhanced for wikidata.
- [http://pythonhosted.org/oursql/](oursql) - MySQL bindings needed for Toolserver scripts (only required for some scripts).


###Scripts

- ```wikidata_blank_items.py``` - Initially designed to find blank items, this exploits a Wikibase bug, and finds duplicate items. (TS)
- ```wikidata_create.py``` - Creates Wikidata items by importing local langlinks. Can easily be imported into other scripts.
- ```wikidata_null_edit.py``` - Performs a "null edit" on a Wikidata item. Can easily be imported into other scripts.
- ```wikidata_redir.py``` - Uses a database query to find items where the sitelink is a redirect. (TS)
- ```wikidata_rc.py``` - Searches the recentchanges table for interwiki.py bots, and updates the Wikidata item. (TS)
- ```wikidata_properties.py``` - Mass-adds properties to items based on Wikipedia categories. Reads from on-wiki page.

###Notes

- All of these scripts are still in beta, and may contain bugs.
- Most are configured for [User:Legobot](https://www.wikidata.org/wiki/User:Legobot)
- The Wikidata API may change at any time, and will require updates to the underlying framework

###License

- All scripts are licensed as [CC-Zero](https://creativecommons.org/publicdomain/zero/1.0).
- A copy is included as ```LICENSE.txt```