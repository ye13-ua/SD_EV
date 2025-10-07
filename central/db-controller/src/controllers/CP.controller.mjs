export class CPController {
    constructor({CPModel}) {
        this.CPModel = CPModel;
    }

    ReadAll = async (req, res) => {
        const CPs = await this.CPModel.ReadAll();
        res.json(CPs);
    }

    Create = async (req, res) => {
        const newCP = await this.CPModel.Create({body: req.body});

        if(newCP) return res.status(201).json(newCP);

        return res.status(400).json({error: "Error al crear nuevo CP"})
    }
    
    //TODO: metodos CRUD?
}