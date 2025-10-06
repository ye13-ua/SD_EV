import { Router } from "express";
import {CPController } from "../controllers/CP.controller.mjs";

export const createCPRouter = ({CPModel}) => {
    const CPRouter = Router();
    const Cpcontroller = new CPController({CPModel: CPModel});

    CPRouter.get("/",Cpcontroller.ReadAll);

    CPRouter.post("/", Cpcontroller.Create);

    return CPRouter;
}