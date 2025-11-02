export class CPController {
    constructor({CPModel}) {
        this.CPModel = CPModel;
    }

    ReadAll = async (req, res) => {
        const readedCPs = await this.CPModel.ReadAll();
        //TODO Renderizar los CPs
        if(!readedCPs) {
            return res.status(400).json({error: "Error al leer CP"})
        } else {
            res.render("cps", {
                readedCPs,
                CP_Central_Status_Socket: process.env.CP_CENTRAL_STATUS_SOCKET
            });
        }        
    }

    ReadAllJSON = async (req, res) => {
        const readedCPs = await this.CPModel.ReadAll();
        //TODO Renderizar los CPs
        if(!readedCPs) {
            return res.status(400).json({error: "Error al leer CP"})
        } else {
            res.status(200).json(readedCPs)
        }        
    }

    Read = async (req, res) => {
        const readedCP = await this.CPModel.Read({id: req.params.id});
        
        if(!readedCP) {
            return res.status(400).json({error: "Error al leer CP"})
        } else {
            res.status(200).json(readedCP)
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