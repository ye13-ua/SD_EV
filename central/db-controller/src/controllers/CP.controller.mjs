export class CPController {
    constructor({CPModule}) {
        this.CPModule = CPModule;
    }

    ReadAll = async (req, res) => {
        const CPs = await this.CPModule.ReadAll();
        res.json(CPs);
    }

    Create = async (req, res) => {
        const newCP = await this.CPModule.Create({body: req.body});

        if(newCP) return res.status(201).json(newCP);

        return res.status(400).json({error: "Error al crear nuevo CP"})
    }
    
    //TODO: metodos CRUD?
}