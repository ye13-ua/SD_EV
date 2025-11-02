import { Router } from "express";
import {CPController } from "../controllers/CP.controller.mjs";

export const createCPRouter = ({CPModel}) => {
    const CPRouter = Router();
    const Cpcontroller = new CPController({CPModel: CPModel});

    CPRouter.get("/",Cpcontroller.ReadAll);

    CPRouter.get("/JSON",Cpcontroller.ReadAllJSON);

    CPRouter.get("/:id",Cpcontroller.Read);

    CPRouter.patch("/:id",Cpcontroller.Update);

    CPRouter.post("/", Cpcontroller.Create);

    return CPRouter;
}