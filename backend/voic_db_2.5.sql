SET @OLD_UNIQUE_CHECKS=@@UNIQUE_CHECKS, UNIQUE_CHECKS=0;
SET @OLD_FOREIGN_KEY_CHECKS=@@FOREIGN_KEY_CHECKS, FOREIGN_KEY_CHECKS=0;
SET @OLD_SQL_MODE=@@SQL_MODE, SQL_MODE='ONLY_FULL_GROUP_BY,STRICT_TRANS_TABLES,NO_ZERO_IN_DATE,NO_ZERO_DATE,ERROR_FOR_DIVISION_BY_ZERO,NO_ENGINE_SUBSTITUTION';

-- -----------------------------------------------------
-- Schema voic_db
-- -----------------------------------------------------
CREATE SCHEMA IF NOT EXISTS `voic_db` ;
USE `voic_db` ;

-- -----------------------------------------------------
-- Table `voic_db`.`court_case`
-- -----------------------------------------------------
CREATE TABLE IF NOT EXISTS `voic_db`.`court_case` (
  `case_number` INT NOT NULL,
  `case_charge` VARCHAR(45) NOT NULL,
  `case_article` VARCHAR(45) NOT NULL,
  `case_verdict` VARCHAR(45) NULL,
  `case_facts` BLOB NULL,
  `case_time_created` DATETIME NOT NULL,
  `case_preceed_number` INT NULL,
  `case_released` TINYINT NOT NULL DEFAULT 0,
  PRIMARY KEY (`case_number`),
  UNIQUE INDEX `case_number_UNIQUE` (`case_number` ASC) VISIBLE,
  INDEX `fk_case_succeed_number_idx` (`case_preceed_number` ASC) VISIBLE,
  CONSTRAINT `fk_case_preceed_number`
    FOREIGN KEY (`case_preceed_number`)
    REFERENCES `voic_db`.`court_case` (`case_number`)
    ON DELETE NO ACTION
    ON UPDATE NO ACTION)
ENGINE = InnoDB;

-- -----------------------------------------------------
-- Table `voic_db`.`court_article`
-- -----------------------------------------------------

CREATE TABLE IF NOT EXISTS `voic_db`.`court_article` (
  `case_number` INT NOT NULL AUTO_INCREMENT,
  `case_article` VARCHAR(45) NOT NULL,
  `case_chapter` VARCHAR(45) NOT NULL,
  `case_verdict` VARCHAR(45) NULL,
  `case_number` INT NOT NULL,
  PRIMARY KEY (id),
  INDEX fk_article_case_number_idx (case_number ASC) VISIBLE,
  CONSTRAINT fk_article_case_number
  FOREIGN KEY (case_number)
  REFERENCES voic_db.court_case (case_number)
  ON DELETE NO ACTION
  ON UPDATE NO ACTION)
ENGINE = InnoDB;

-- -----------------------------------------------------
-- Table `voic_db`.`court_user`
-- -----------------------------------------------------
CREATE TABLE IF NOT EXISTS `voic_db`.`court_user` (
  `user_name` VARCHAR(45) NOT NULL,
  `user_first` VARCHAR(45) NOT NULL,
  `user_last` VARCHAR(45) NOT NULL,
  `user_level` VARCHAR(45) NOT NULL,
  `user_created` DATETIME NOT NULL,
  `user_password` VARCHAR(200) NOT NULL,
  `user_phone` VARCHAR(45) NOT NULL,
  `user_question` VARCHAR(45) NOT NULL,
  `user_answer` VARCHAR(45) NOT NULL,
  `user_address1` VARCHAR(90) NULL,
  `user_address2` VARCHAR(90) NULL,
  `user_postcode` VARCHAR(45) NULL,
  `user_token` VARCHAR(45) NOT NULL,
  PRIMARY KEY (`user_name`),
  UNIQUE INDEX `user_name_UNIQUE` (`user_name` ASC) VISIBLE)
ENGINE = InnoDB;

-- -----------------------------------------------------
-- Table `voic_db`.`court_docs`
-- -----------------------------------------------------
CREATE TABLE IF NOT EXISTS `voic_db`.`court_docs` (
  `docs_title` VARCHAR(45) NOT NULL,
  `docs_path` VARCHAR(200) NOT NULL,
  `docs_type` VARCHAR(45) NOT NULL,
  `docs_approved` TINYINT NOT NULL DEFAULT 0,
  `docs_case` INT NULL,
  `docs_author` VARCHAR(45) NOT NULL,
  UNIQUE INDEX `docs_path_UNIQUE` (`docs_path` ASC) VISIBLE,
  PRIMARY KEY (`docs_title`),
  UNIQUE INDEX `docs_title_UNIQUE` (`docs_title` ASC) VISIBLE,
  INDEX `fk_docs_case_idx` (`docs_case` ASC) VISIBLE,
  INDEX `fk_docs_author_idx` (`docs_author` ASC) VISIBLE,
  CONSTRAINT `fk_docs_case`
    FOREIGN KEY (`docs_case`)
    REFERENCES `voic_db`.`court_case` (`case_number`)
    ON DELETE NO ACTION
    ON UPDATE NO ACTION,
  CONSTRAINT `fk_docs_author`
    FOREIGN KEY (`docs_author`)
    REFERENCES `voic_db`.`court_user` (`user_name`)
    ON DELETE NO ACTION
    ON UPDATE NO ACTION)
ENGINE = InnoDB;


-- -----------------------------------------------------
-- Table `voic_db`.`junction_case_user`
-- -----------------------------------------------------
CREATE TABLE IF NOT EXISTS `voic_db`.`junction_case_user` (
  `junction_user` VARCHAR(45) NOT NULL,
  `junction_case` INT NOT NULL,
  `junction_role` VARCHAR(45) NOT NULL,
  PRIMARY KEY (`junction_user`, `junction_case`),
  INDEX `fk_junction_case_idx` (`junction_case` ASC) VISIBLE,
  CONSTRAINT `fk_junction_user`
    FOREIGN KEY (`junction_user`)
    REFERENCES `voic_db`.`court_user` (`user_name`)
    ON DELETE NO ACTION
    ON UPDATE NO ACTION,
  CONSTRAINT `fk_junction_case`
    FOREIGN KEY (`junction_case`)
    REFERENCES `voic_db`.`court_case` (`case_number`)
    ON DELETE NO ACTION
    ON UPDATE NO ACTION)
ENGINE = InnoDB;


SET SQL_MODE=@OLD_SQL_MODE;
SET FOREIGN_KEY_CHECKS=@OLD_FOREIGN_KEY_CHECKS;
SET UNIQUE_CHECKS=@OLD_UNIQUE_CHECKS;
