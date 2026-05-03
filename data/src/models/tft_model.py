import torch
import torch.nn as nn


class TFTAutoencoder(nn.Module):
    def __init__(self, input_size, hidden_size, num_heads, num_layers, dropout):
        super().__init__()

        self.encoder = nn.LSTM(
            input_size,
            hidden_size,
            num_layers=num_layers,
            batch_first=True,
            dropout=dropout
        )

        self.attention = nn.MultiheadAttention(
            embed_dim=hidden_size,
            num_heads=num_heads,
            dropout=dropout,
            batch_first=True
        )

        self.decoder = nn.LSTM(
            hidden_size,
            hidden_size,
            num_layers=num_layers,
            batch_first=True,
            dropout=dropout
        )

        self.output_layer = nn.Linear(hidden_size, input_size)

    def forward(self, x):
        # x: (batch, seq_len, features)

        enc_out, _ = self.encoder(x)

        attn_out, _ = self.attention(enc_out, enc_out, enc_out)

        dec_out, _ = self.decoder(attn_out)

        recon = self.output_layer(dec_out)

        return recon
