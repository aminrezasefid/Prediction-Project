import torch
import torch.nn as nn
import torch_geometric.nn as gnn
activations = {
    'relu': nn.ReLU(),
    'tanh': nn.Tanh(),
    'leaky': nn.LeakyReLU()
}

class GNNModel(torch.nn.Module):
    def __init__(self, n_nodes, embed_dim=10, n_conv=3, conv_dims=(32, 32, 32, 16), n_dense=5, dense_dims=(8, 8, 8, 8,8),
                 act_f='leaky',n_relation=2,aggr='add',target_dim = 3):
        super(GNNModel, self).__init__()
        self.target_dim=target_dim
        self.embed_dim = embed_dim 
        self.n_conv = n_conv
        self.conv_dims = conv_dims
        self.n_dense = n_dense
        self.activation = activations[act_f]
        self.n_nodes = n_nodes
        self.n_relation=n_relation
        self.embedding = torch.nn.Embedding(num_embeddings=n_nodes, embedding_dim=embed_dim)
        conv_layers = [gnn.RGCNConv(self.embed_dim, self.conv_dims[0],self.n_relation,aggr=aggr)]
        for i in range(n_conv - 1):
            conv_layers.append(gnn.RGCNConv(conv_dims[i], conv_dims[i + 1],self.n_relation,aggr=aggr))
        self.conv_layers =nn.ModuleList(conv_layers)
        lin_layers = []
        lin_layers.append(torch.nn.Linear(conv_dims[n_conv - 1]*2, dense_dims[0]))
        for i in range(n_dense - 2):
            lin_layers.append(torch.nn.Linear(dense_dims[i], dense_dims[i + 1]))
        lin_layers.append(torch.nn.Linear(dense_dims[n_dense - 2], self.target_dim))
        self.lin_layers = nn.ModuleList(lin_layers)
        self.out = nn.LogSoftmax(dim=1)
        self.drop = nn.Dropout(p=0.1)
    def forward(self,data,home, away):
        edge_index,edge_type=data.edge_index,data.edge_type

        x = torch.tensor(list(range(self.n_nodes)))
        x = self.embedding(x).reshape(-1, self.embed_dim)

        x = self.conv_layers[0](x, edge_index,edge_type)
        x = self.activation(x)
        x = self.drop(x)

        for i in range(self.n_conv - 1):
            x = self.activation(self.conv_layers[i + 1](x, edge_index,edge_type))
            x = self.drop(x)
        x = torch.cat([x[home], x[away]], dim=1)
        for i in range(self.n_dense):
            x = self.activation(self.lin_layers[i](x))
            x = self.drop(x)
        x = self.out(x)
        return x.reshape(-1, self.target_dim)
                
