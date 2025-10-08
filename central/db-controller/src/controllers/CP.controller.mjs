export class CPController {
    constructor({CPModel}) {
        this.CPModel = CPModel;
    }

    ReadAll = async (req, res) => {
        const readedCPs = await this.CPModel.ReadAll();
       
        if(!readedCPs) {
            return res.status(400).json({error: "Error al leer CP"})
        } else if (readedCPs.error) {
            return res.status(400).json({error: readedCPs.error})
        } else {
            return res.status(201).json(readedCPs);
        }        
    }

    Create = async (req, res) => {
        const newCP = await this.CPModel.Create({body: req.body});

        if(!newCP) {
            return res.status(400).json({error: "Error al crear nuevo CP"})
        } else if (newCP.error) {
            return res.status(400).json({error: newCP.error})
        } else {
            return res.status(201).json(newCP);
        }        
    }
    
    //TODO: metodos CRUD?
}