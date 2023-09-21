SELECT Count(DISTINCT uid) as Count FROM `validation.validation_table`  WHERE STARTS_WITH(case_id, @LABEL)
