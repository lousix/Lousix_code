/**
 * @name Path traversal (signal)
 * @description Potential path traversal risk
 * @id java/path-injection
 * @kind problem
 * @problem.severity warning
 * @precision medium
 */

 import java

 from Method m
 where m.hasName("readFile")
 select m, "Potential path traversal risk."
 