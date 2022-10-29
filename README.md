# TODO

* [x] Add bank column
* [x] Receive file_path, user_id, user_account and bank as input
* [x] Log messages
* [x] Try catch
* [x] Separate data NORMALIZATION from LOAD and PERSISTENCE
* [x] Organize classes and methods
* [ ] `IGNORED` Import Nubank `Nubank has not an statement becouse I use it only for credit card`
* [x] Import Inters Full history
* [x] Automated tests
* [x] Lint
* [x] Github
* [x] `bonus` REPL
* [x] Add categorization of transaction
* [x] Add encapsulation `isolate spending by user context`
* [x] Add category rules `automatic set category`
* [x] Update unit tests not dependent from db
* [ ] Update unit tests dependent from db
* [ ] Split import table from transactions table
* [ ] Make import command cleanup the table after execution
* [ ] Reprocess categorization transactions
* [ ] Run reprocess categorization after create or update category or category_rule
* [ ] Import part statement `avoid duplication using the date`
* [ ] Add categorization per transaction `in separated table because of the reprocessment of categorization`
* [ ] Statement report by date `begin and end`
* [ ] Grouped statement report by date `begin and end`
* [ ] Grouped graph report `many months`

* [ ] Avoid category duplication
* [ ] On creating category rule select category by name cas insensitivity
* [ ] Separate file load from data_frame manipulation
* [ ] Remove "set X of many" feature
* [ ] Use IMDB (in-memory database) for unit tests
* [ ] DocString


# UNIT TESTS

* [ ] `inter_import_csv_load` Basic import test (depends on DB)
* [ ] `inter_import_df_save` Basic (depends on DB)

* [x] `data_frame` Create user id column
* [x] `data_frame` Create user account column
* [x] `data_frame` Create bank column
* [x] `data_frame` Create category column
* [x] `data_frame` format date column
* [x] `data_frame_category` When category matches, set category column
* [x] `data_frame_category` When no category matches, set category column as None
* [x] `data_frame_category` When find more than 1 category matches, add Error
* [x] `data_frame_category` When many category error, show them all thogether

* [ ] `category_save` Basic (depends on DB)
* [ ] `category_fetch_by_name` Basic (depends on DB)

* [ ] `category_rule_save` Basic (depends on DB)
* [ ] `category_rule_create` Happy flow (depends on DB)
* [ ] `category_rule_create` When no category found, error (depends on DB)

* [ ] `transaction_set_context` One (depends on DB)
* [ ] `transaction_set_context` Many `separated by space` (depends on DB)

<!-- DATA BASE SETUP FOR PYTEST -->
<!-- https://smirnov-am.github.io/pytest-testing_database/ -->