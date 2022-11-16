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
* [x] Update unit tests dependent from db
* [x] Split import table from transactions table
* [x] Make import command cleanup the table after execution
* [x] Import part statement `avoid duplication using the date`
* [x] Reprocess categorization transactions
* [x] Run reprocess categorization after create or update category or category_rule
* [x] Add categorization per transaction `in separated table because of the reprocessment of categorization`

* [ ] `visualization - dash` Statement report by date `begin and end`
* [ ] `visualization - dash` Grouped statement report by date `begin and end`
* [ ] `visualization - dash` Grouped graph report `many months`

* [ ] Annul some spend(s) based on a gain(s)
* [ ] Create groups of categories (Like essesials and etc)

* [ ] Avoid category duplication
* [ ] On creating category rule select category by name cas insensitivity
* [ ] Separate file load from data_frame manipulation
* [ ] Remove "set X of many" feature
* [ ] Use IMDB (in-memory database) for unit tests
* [ ] DocString


# Answer theese questions with features
* [ ] How much did I spent `filter month`?
* [ ] How much did I spent per sector (essensial and etc) `filter month`?
* [ ] How much did I spent per category `filter month`?
* [ ] How much did I took off from investment `filter month`?
