Changes
=======

Version 0.11.0 (released 2021-04-22)
-----------------------------------
- Add missing languages for all CERN member states

Version 0.10.0 (released 2021-03-28)
-----------------------------------
- Add Slovene language

Version 0.9.0 (released 2018-06-04)
-----------------------------------
- Remove the DOI from the required fields

Version 0.8.0 (released 2018-05-14)
-----------------------------------

- Addition of internal_* and Press fields.
- Fix language ISO 639-2 vs 639-3 mix on DoJSON translations.

Version 0.7.0 (released 2018-04-03)
-----------------------------------

- Addition of default language for videos (English)

Version 0.6.0 (released 2017-12-08)
-----------------------------------

- Videos release candidate.
- New ignore fields: 962__n, 852__j, 778, 981__a.
- New 'audio_characteristics' field.
- Addition of new languages: Ukrainian, Turkish, etc.
- Ignore older video presets.
- Ignore contributor field, if there is no $a subfield.
- Fix translation of unicode roles.
- Fix one contributor several roles.

Version 0.5.0 (released 2017-09-14)
-----------------------------------

Version 0.4.1 (released 2017-08-28)
-----------------------------------

Version 0.4.0 (released 2017-08-18)
-----------------------------------

Version 0.3.2 (released 2016-08-12)
-----------------------------------

- First draft video schema.
- Moves ``schemas`` folder up as they don't relay anymore on MACR21 as base
  model.


Version 0.3.0 (released 2016-04-27)
-----------------------------------

- Add jsonschemas for all custom fields and for the models.
- Adds ``$schema`` key after performing the transformation depending on
  the model used.

Version 0.2.0 (released 2016-02-29)
-----------------------------------

- Initial public release.
