# TODO
* [ ] Use https://www.mage.ai/
* [x] Add bank column
* [x] Receive file_path, user_id, user_account and bank as input
* [x] Log messages
* [x] Try catch
* [x] Separate data NORMALIZATION from LOAD and PERSISTENCE
* [x] Organize classes and methods
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
* [x] Annul some spend(s) based on gain(s)
* [x] Create groups of categories (Like essesials and etc)
* [ ] Remove Outros Category
* [ ] Avoid category duplication
* [ ] Add priority on category to sort by it
* [ ] ~~Remove "set X of many" feature~~

# Visualization
* [x] Statement report by date `begin and end`
* [x] Grouped statement report by date `begin and end`
* [x] Grouped graph report `many months`
* [x] See every month in the same table
* [x] Align numbers at right
* [ ] Money format
* [ ] `all month` Hover on one month in all months` table to show percentage of diference between last value
* [ ] `all month` Select a category and shows it on graph comparing all months and other things
* [ ] `all month` Add total in every month
* [ ] Set filters on url
* [ ] Use dash pages

# Answer theese questions with features
* [x] How much did I spent `filter month`?
* [x] How much did I spent per sector (essensial and etc) `filter month`?
* [x] How much did I spent per category `filter month`?
* [x] How much did I took off from investment `filter month`?

# Technical things
* [x] Separate file load from data_frame manipulation
* [ ] On creating category rule select category by name case insensitivity
* [ ] DocString
* [ ] Use python Decimal in everything to avoid rounding errors
* [ ] Set some tests to use decimal values
* [ ] Add Prettier
* [ ] ~~Use IMDB (in-memory database) for unit tests~~

# Priority
* [ ] Turn poc dashoboard into a feature with tests and etc
* [ ] Add grouped context spends on dashboard
* [ ] Import Nubank
* [ ] Feature of transaction substitution
