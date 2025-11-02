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
    
    Update = async (req, res) => {
        
        
        const actualizacion = {
            ID_UUID: req.params.id,
            Precio_KWH: req.body.Precio_KWH,
        }
        
        const CPactualizado = await this.CPModel.Update({body: actualizacion});
        
        if(!CPactualizado) {
            return res.status(400).json({error: "Error al actualizar CP"})
        } else if (CPactualizado.error) {
            return res.status(400).json({error: CPactualizado.error})
        } else {
            return res.status(201).json(CPactualizado);
        }

    }

    //TODO: metodos CRUD?
}