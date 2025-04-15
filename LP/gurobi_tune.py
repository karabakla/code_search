from gurobipy import * # type: ignore
model = read("outputs/models/Extended_LCD_ILP_2_19_4_8.mps")

model.params.TuneCriterion = 2

# tune count to 100
model.params.TuneResults = 1
model.params.TuneTimeLimit = 3600

model.params.Quad = 1
model.params.NumericFocus = 3

model.tune()

if model.tuneResultCount > 0:
    for i in range(model.tuneResultCount):
        model.getTuneResult(i)
        model.write(f"outputs/models/Extended_LCD_ILP_2_19_4_8_tuned.prm")