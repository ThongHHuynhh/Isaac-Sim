import omni

# Get the stage
stage = omni.usd.get_context().get_stage()
# Get the prim object
prim = stage.GetPrimAtPath("/World/A_900023_INT_00_16_JUL_25_1/tn__A900023INT0016JUL251_lT8CFIMq0/tn__3453A0001_zH/tn__3453A0102_zH/tn__IRB12005091_pG9Pc5/tn__IRB1200509base_stan1_rT9CZ0i9/NONE")
# print all the attributes of the prim
print(prim.GetAttributes())
# print the orient
print(prim.GetAttribute("xformOp:orient").Get())
# print the translation
print(prim.GetAttribute("xformOp:translate").Get())