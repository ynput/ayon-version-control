Perforce trigger
================

This trigger(s) provides connection between Perforce and AYON server.

Currently it is implemented "submit-change" trigger which engages before any commit. 
This should result in calling specific endpoint on AYON server which will create
event from provided submit information (user, changelist, client).

This event might be later consumed and start AYON based automatization.

Attached script must be committed to Perforce depot which should be observed AND
trigger created by perforce user with admin permissions via `p4 triggers`.

Format of added trigger description (at the bottom of shown form, tab at beginning of line):
```
	ayon_change_submit change-submit //streamsDepot/... "python3 %//streamsDepot/mainline/Triggers/change_submit_trigger.py% %change% %user% %client%"
```
where `streamsDepot` is name of observed Perforce depot, `//streamsDepot/mainline/Triggers` is path
where `change_submit_trigger.py` is committed.

(Requires `python3` available on Perforce server machine.)