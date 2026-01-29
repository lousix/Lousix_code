/**
 * @name Test WebGoat Database
 * @description Simple test to check if database is working
 * @id java/test-webgoat
 * @kind test
 */

import java

from Method m
select m, "Method: " + m.getName() + " in class: " + m.getDeclaringType().getName()
